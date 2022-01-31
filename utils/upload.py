import boto3
import os
import sys
from dotenv import load_dotenv
load_dotenv()

sys.path.append(os.path.abspath('../'))
import log

logger = log.get_logger("pablo")


AWS_BUCKET_NAME = os.environ.get('AWS_BUCKET_NAME')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_ACCESS_SECRET = os.environ.get('AWS_ACCESS_SECRET')

OUTPUT_FOLDER = 'output'


class FileUpload:
    def __init__(self):
        session = boto3.Session(
            aws_access_key_id = AWS_ACCESS_KEY_ID,
            aws_secret_access_key = AWS_ACCESS_SECRET,
        )
        s3 = session.resource('s3')
        self.bucket = s3.Bucket(AWS_BUCKET_NAME)
        self.path = os.path.join(os. getcwd(), 'output')


    def upload(self, filePath):
        with open(filePath, 'rb') as data:
            self.bucket.put_object(Key=filePath[len(self.path)+1:], Body=data)
            logger.info(' Uploaded #' + str(filePath))

    def upload_files(self):

        for subdir, dirs, files in os.walk(self.path):
            for file in files:
                full_path = os.path.join(subdir, file)
                with open(full_path, 'rb') as data:
                    self.bucket.put_object(Key=full_path[len(self.path)+1:], Body=data)
                logger.info("Uploaded file "+ str(file))

        logger.info("Uploaded all files to S3 successfully")


if __name__ == '__main__':

    logger.info("Uploading {0} to {1}".format(OUTPUT_FOLDER, AWS_BUCKET_NAME))
    fileupload = FileUpload()
    fileupload.upload_files()


