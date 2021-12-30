import pytest
from tests.metallize_helpers.cmd import MetallizeTest

test = MetallizeTest(__file__, 'ubuntu20-ext4.yaml')

@pytest.fixture
def cleanup():
    test.setup()
    yield
    test.cleanup()

def test_build_from_ext_dir(cleanup):
    test.generate_config_from_template()
    test.run_metallize()
    test.run_qemu(checker_f=lambda output: output.find('localhost login') != -1, legacy_or_uefi="legacy")