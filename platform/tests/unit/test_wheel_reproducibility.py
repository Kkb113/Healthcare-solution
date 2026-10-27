import base64
import csv
import hashlib
import io
import zipfile

import pytest
from canonicalize_platform_wheel import canonicalize


def test_host_newlines_permissions_and_zip_order_do_not_change_final_wheel(tmp_path):
    paths = [tmp_path / "windows.whl", tmp_path / "linux.whl"]
    prefix = "intellify_healthcare_platform-0.2.3.dist-info/"
    for index, path in enumerate(paths):
        metadata = b"Name: intellify-healthcare-platform\nVersion: 0.2.3\n"
        if index == 0:
            metadata = metadata.replace(b"\n", b"\r\n")
        contents = [
            ("hcp/__init__.py", b"# unchanged source\n"),
            (prefix + "METADATA", metadata),
            (prefix + "RECORD", b"old hashes"),
        ]
        with zipfile.ZipFile(path, "w") as archive:
            for name, content in contents[:: (-1 if index else 1)]:
                info = zipfile.ZipInfo(name)
                info.create_system = index * 3
                info.external_attr = (0o100666 if index else 0o100777) << 16
                archive.writestr(info, content)
        canonicalize(path)
    assert paths[0].read_bytes() == paths[1].read_bytes()
    with zipfile.ZipFile(paths[0]) as archive:
        for name, digest, length in csv.reader(
            io.StringIO(archive.read(prefix + "RECORD").decode())
        ):
            if name.endswith("/RECORD"):
                assert digest == length == ""
            else:
                data = archive.read(name)
                assert (
                    digest
                    == "sha256="
                    + base64.urlsafe_b64encode(hashlib.sha256(data).digest())
                    .rstrip(b"=")
                    .decode()
                )
                assert int(length) == len(data)


def test_unsafe_archive_is_rejected_without_writing_extracted_paths(tmp_path):
    path = tmp_path / "unsafe.whl"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("../escape.py", b"unsafe")
    with pytest.raises(ValueError, match="unsafe"):
        canonicalize(path)
    assert not (tmp_path.parent / "escape.py").exists()
