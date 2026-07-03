from pydantic import BaseModel, Field


class MinioObject(BaseModel):
    """
    Uploaded object details.
    """

    key: str = Field(..., alias="key")
    size: int | None = Field(default=0)


class MinioBucket(BaseModel):
    """
    Bucket information.
    """

    name: str = Field(..., alias="name")


class MinioS3(BaseModel):
    """
    S3 payload.
    """

    bucket: MinioBucket
    object: MinioObject


class MinioRecord(BaseModel):
    """
    Single event record.
    """

    eventName: str
    s3: MinioS3


class MinioEvent(BaseModel):
    """
    Complete webhook payload received from MinIO.
    """

    Records: list[MinioRecord]

    @property
    def record(self) -> MinioRecord:
        """
        Return the first record.
        """

        return self.Records[0]

    @property
    def bucket_name(self) -> str:
        """
        Bucket name.
        """

        return self.record.s3.bucket.name

    @property
    def object_name(self) -> str:
        """
        Uploaded object path.
        """

        return self.record.s3.object.key

    @property
    def event_name(self) -> str:
        """
        Event type.
        """

        return self.record.eventName

    @property
    def file_size(self) -> int:
        """
        Uploaded file size.
        """

        return self.record.s3.object.size