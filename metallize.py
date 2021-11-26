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
        cmds.append(f"DOCKER_BUILDKIT=1 docker build {prev_img_str} {build_args} -t {image} -f {src_file} {context}")
        prev_img = image
    cmds.append(cmds[-1] + f" --output type=tar,dest=- | tar --delete etc/resolv.conf  > {tar_file}" )
    cmds.append(f"(cd {build_path} && mkdir -p etc && ln -sf /run/systemd/resolve/resolv.conf etc/resolv.conf)")
    cmds.append(f"tar -rvf {tar_file} -C {build_path} etc/resolv.conf")
    return cmds

USER_VAR='--user `id -u`:`id -g`'
def build_squashfs(config, tar_file: Path, squashfs_file: Path, images_path: Path, project_path: Path):
    live_path = squashfs_file.parent
    generator = config['output']['generator']
    cmds = [
        f"mkdir -p {live_path}",
        f"DOCKER_BUILDKIT=1 docker build -t {generator} -f {images_path / generator} {project_path}",
        f"rm -f {squashfs_file}",
	    (
            f"tar --wildcards --delete 'boot/*' < {tar_file} | "
            f"docker run -i -v {live_path.absolute()}:/tmp {USER_VAR} {generator} "
            f"mksquashfs - /tmp/{squashfs_file.name}  -comp {config['args']['compression']} -b 1024K -always-use-fragments -keep-as-directory -no-recovery -exit-on-error -tar "
        )
    ]
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

def generate(config, images_path: Path, build_path:Path, iso_src_path:Path, boot_path:Path, project_path: Path):
    output_path = build_path / config['output']['output-file']
    config_output_generator = config['output']['generator']

    cmds = [
        f"DOCKER_BUILDKIT=1 docker build -t {config_output_generator} -f {images_path / config_output_generator} {project_path}",
        (
            f"docker run {USER_VAR} "
            f"-v {boot_path.absolute()}:/boot "
            f"-v {iso_src_path.absolute()}:/iso_src "
            f"-v {output_path.parent.absolute()}:/out "
            f"{config_output_generator} /build.sh {output_path.name}"
        )
    ]
    return cmds

def main(config_file, extension_dir):
    project_path = Path(os.path.dirname(os.path.realpath(__file__)))
    config_file_path = Path(config_file)
    config = yaml.load(open(config_file_path), Loader=yaml.SafeLoader)
    config_metallize = config['metallize'] = config.get('metallize', {})
    config_metallize['dockerfile_dir'] = config_metallize.get('dockerfile_dir', project_path / 'docker')
    config_metallize['build_dir'] = config_metallize.get('build_dir', 'build')
    config_args = config['args'] = config.get('args', {})
    config_args['compression'] = config_args.get('compression', 'lzma')
    build_path = Path(config_metallize['build_dir'])
    images_path = Path(config_metallize['dockerfile_dir'])
    extension_path = Path(extension_dir)
    tar_file = build_path / f"{config_file_path.name}.tar"
    iso_src_path = build_path / "iso_src"
    squashfs_file = iso_src_path / "live" / f"rootfs.squashfs"
    boot_path = iso_src_path / "boot"

    cmds = (
        ["set -x -e"]
        + build_tar(config, images_path, build_path, extension_path, project_path, tar_file)
        + build_squashfs(config, tar_file, squashfs_file, images_path, project_path)
        + extract_kernel_files(boot_path, tar_file)
        + generate(config, images_path, build_path, iso_src_path, boot_path, project_path)
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

    if not is_docker_installed():
        print("You should have docker with version 18.09 or more", file=sys.stderr)
        sys.exit(1)

    main(args.config_file, args.extensions_dir)
