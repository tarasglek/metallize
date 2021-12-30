#!/usr/bin/env python3
"""
metallize.py config.yaml
"""
import os
import yaml
import sys
import argparse
from pathlib import Path

def fail(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)

"""
Takes list of docker file and produces a tar file rootfs
does some magic for /etc/resolv.conf, as the one from docker build will almost-certainly be wrong
"""
def build_tar(config, images_path, build_path, extensions_path, project_path, tar_file):
    images_ls = config['images']
    cmds = [
        "#" + str(config),
        "mkdir -p " + str(build_path)
    ]
    config_args = config['args']
    build_args = " ".join([f"--build-arg METALLIZE_{key.upper()}={value}" for (key, value) in config_args.items()])
    prev_img = None
    for i, image in enumerate(images_ls):
        src_file = extensions_path / image if (extensions_path / image).exists() else images_path / image
        context = extensions_path if (extensions_path / image).exists() else project_path
        if not src_file.exists():
            if i == 0:
                cmds.append("docker pull " + image)
                prev_img = image
                continue
            else:
                fail(f"No file named '{src_file}' exists")
        prev_img_str = f"--build-arg METALLIZE_SRC_IMG='{prev_img}'" if prev_img else ""
        tag = image
        # make for a pretty name of the final docker image
        if i == len(images_ls) - 1:
            tag = Path(tar_file).stem.split('.')[0]
        cmds.append(f"DOCKER_BUILDKIT=1 docker build {prev_img_str} {build_args} -t {tag} -f {src_file} {context}")
        prev_img = tag
    cmds.append(cmds[-1] + f" --output type=tar,dest=- | tar --delete etc/resolv.conf  > {tar_file}" )
    cmds.append(f"(cd {build_path} && mkdir -p etc && ln -sf /run/systemd/resolve/resolv.conf etc/resolv.conf)")
    cmds.append(f"tar -rvf {tar_file} -C {build_path} etc/resolv.conf")
    return cmds

def extract_kernel_files(boot_path: Path, tar_file: Path):
    cmds = [
        f"mkdir -p {boot_path}",
        (
	        f"tar --show-transformed-names --transform='s:-.*::' --transform='s:.*/::' -xvf {tar_file} -C {boot_path} "
		    '--wildcards "boot/vmlinuz-*" '
		    '--wildcards "boot/initrd*-*"'
        )
    ]
    return cmds

def generate_generic(config, generator_name:str, generator_docker_path:Path, tar_file:Path, output_file_path:Path, project_path: Path):
    output_file = output_file_path.absolute()
    cmds = [
        f"DOCKER_BUILDKIT=1 docker build -t {generator_name} -f {generator_docker_path} {project_path}",
        f"rm -f {output_file}",
        f"touch {output_file}",
        (
        f"docker run "
            f"-v {tar_file.absolute()}:/input.tar "
            f"-v {output_file}:/output.file "
            f"--privileged "
            f"{generator_name} /build.cmd /input.tar /output.file {config['output']['kernel_boot_params']}"
        )
    ]
    return cmds

def load_config(project_path, config_file_path, default_built_dir='build'):
    config = yaml.load(open(config_file_path), Loader=yaml.SafeLoader)
    config_metallize = config['metallize'] = config.get('metallize', {})
    config_metallize['dockerfile_dir'] = config_metallize.get('dockerfile_dir', str((project_path / 'docker')))
    config_metallize['build_dir'] = config_metallize.get('build_dir', default_built_dir)
    config_args = config['args'] = config.get('args', {})
    config_args['compression'] = config_args.get('compression', 'lzma')
    config_output = config['output']
    config_output['kernel_boot_params'] = config_output.get('kernel_boot_params',
        'nomodeset console=ttyS0,115200 console=tty0' )
    return config
    
def main(config_file, extension_dir):
    project_path = Path(os.path.dirname(os.path.realpath(__file__)))
    config_file_path = Path(config_file)
    config = load_config(project_path, config_file_path)
    config_metallize = config['metallize']
    build_path = Path(config_metallize['build_dir'])
    extension_path = Path(extension_dir)
    images_path = Path(config_metallize['dockerfile_dir'])
    tar_file = build_path / f"{config_file_path.name}.tar"
    output_file =  build_path / config['output']['file']
    generators = {
        "ext4": images_path / "ext4-generator.dockerfile",
        "livecd": images_path / "livecd-generator.dockerfile",
    }
    generator_name = config['output']['generator']
    generator_docker_path = generators[generator_name]
    cmds = (
        ["set -x -e"]
        + build_tar(config, images_path, build_path, extension_path, project_path, tar_file)
        + generate_generic(config, generator_name, generator_docker_path, tar_file, output_file, project_path)
    )
    print("\n".join(cmds))


def is_docker_installed():
    import subprocess
    try:
        version = subprocess.check_output("docker version --format '{{.Server.Version}}'", shell=True)
    except subprocess.CalledProcessError:
        return False

    version = version.decode('ascii')
    version = version.split('.')

    if int(version[0]) > 18:
        return True
    elif int(version[0]) == 18 and int(version[1]) >= 9:
        return True

    return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file', help='yaml file with configs')
    parser.add_argument('--extensions_dir', help='path to dir with extension', default='metallize')
    args = parser.parse_args()

    if sys.platform != "linux" and sys.platform != "linux2":
        print("Now metallize works only on linux platform", file=sys.stderr)
        sys.exit(1)

    if not is_docker_installed():
        print("You should have docker with version 18.09 or more", file=sys.stderr)
        sys.exit(1)

    main(args.config_file, args.extensions_dir)
