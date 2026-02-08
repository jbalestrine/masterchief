from tf_wizard.generator import generate_module_zip, generate_files
import zipfile
import io


def test_generate_basic():
    spec = {
        "module_name": "testmod",
        "provider": "aws",
        "variables": [{"name": "region", "type": "string", "default": "us-east-1"}],
        "resources": [{"type": "aws_s3_bucket", "name": "bucket", "args": {"bucket": "test-bucket"}}],
        "outputs": [{"name": "bucket_id", "value": "aws_s3_bucket.bucket.id"}],
    }
    b = generate_module_zip(spec)
    z = zipfile.ZipFile(io.BytesIO(b))
    assert "main.tf" in z.namelist()
    assert "variables.tf" in z.namelist()
    assert "outputs.tf" in z.namelist()
