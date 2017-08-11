# -*- coding=utf-8
import random
import sys
import os
from cos_client import CosS3Client
from cos_client import CosConfig
from cos_exception import CosServiceError

ACCESS_ID = os.environ["ACCESS_ID"]
ACCESS_KEY = os.environ["ACCESS_KEY"]


def gen_file(path, size):
    _file = open(path, 'w')
    _file.seek(1024*1024*size)
    _file.write('cos')
    _file.close()


def setUp():
    print "start test"


def tearDown():
    print "function teardown"


def Test():
    conf = CosConfig(
        Appid="1252448703",
        Region="cn-north",
        Access_id=ACCESS_ID,
        Access_key=ACCESS_KEY
    )
    client = CosS3Client(conf)

    test_bucket = 'test01'
    file_size = 2  # 方便CI通过
    file_id = str(random.randint(0, 1000)) + str(random.randint(0, 1000))
    file_name = "tmp" + file_id + "_" + str(file_size) + "MB"

    print "Test Copy Object From Other Bucket "
    response = client.list_buckets()

    copy_source = {'Bucket': 'test01', 'Key': '/test.txt'}
    print "Test Copy Object From Other Bucket "
    response = client.copy_object(
            Bucket='test04',
            Key='test.txt',
            CopySource=copy_source
           )
    print response

    print "Test Put Object That Bucket Not Exist " + file_name
    try:
        response = client.put_object(
            Bucket='test0xx',
            Body='T'*1024*1024,
            Key=file_name,
            CacheControl='no-cache',
            ContentDisposition='download.txt'
        )
    except CosServiceError as e:
        print e.get_origin_msg()
        print e.get_digest_msg()
        print e.get_status_code()
        print e.get_error_code()
        print e.get_error_msg()
        print e.get_resource_location()
        print e.get_trace_id()
        print e.get_request_id()

    special_file_name = "对象()*'/. 存![]^&*~储{|}~()"
    print "Test Put Object Contains Special Characters " + special_file_name
    response = client.put_object(
            Bucket=test_bucket,
            Body='S'*1024*1024,
            Key=special_file_name,
            CacheControl='no-cache',
            ContentDisposition='download.txt'
        )

    print "Test Get Object Contains Special Characters " + special_file_name
    response = client.get_object(
            Bucket=test_bucket,
            Key=special_file_name,
        )

    print "Test Delete Object Contains Special Characters " + special_file_name
    response = client.delete_object(
        Bucket=test_bucket,
        Key=special_file_name
    )

    print "Test Put Object " + file_name
    gen_file(file_name, file_size)
    fp = open(file_name, 'rb')
    response = client.put_object(
            Bucket=test_bucket,
            Body=fp,
            Key=file_name,
            CacheControl='no-cache',
            ContentDisposition='download.txt'
        )
    fp.close()
    os.remove(file_name)

    print "Test Get Object " + file_name
    response = client.get_object(
            Bucket=test_bucket,
            Key=file_name,
        )
    # 返回一个generator
    # stream_generator = response['Body'].get_stream(stream_size=1024*512)
    response['Body'].get_stream_to_file('cos.txt')
    if os.path.exists('cos.txt'):
        os.remove('cos.txt')

    print "Test Head Object " + file_name
    response = client.head_object(
        Bucket=test_bucket,
        Key=file_name
    )

    print "Test Delete Object " + file_name
    response = client.delete_object(
        Bucket=test_bucket,
        Key=file_name
    )

    print "Test List Objects"
    response = client.list_objects(
        Bucket=test_bucket
    )

    print "Test Create Bucket"
    response = client.create_bucket(
            Bucket='test'+file_id,
            ACL='public-read'
        )

    print "Test Delete Bucket"
    response = client.delete_bucket(
        Bucket='test'+file_id
    )

    print "Test Create MultipartUpload"
    response = client.create_multipart_upload(
        Bucket=test_bucket,
        Key='multipartfile.txt',
    )
    uploadid = response['UploadId']

    print "Test Abort MultipartUpload"
    response = client.abort_multipart_upload(
        Bucket=test_bucket,
        Key='multipartfile.txt',
        UploadId=uploadid
    )

    print "Test Create MultipartUpload"
    response = client.create_multipart_upload(
        Bucket=test_bucket,
        Key='multipartfile.txt',
    )
    uploadid = response['UploadId']

    print "Test Upload Part1"
    response = client.upload_part(
        Bucket=test_bucket,
        Key='multipartfile.txt',
        UploadId=uploadid,
        PartNumber=1,
        Body='A'*1024*1024*10
    )

    print "Test Upload Part2"
    response = client.upload_part(
        Bucket=test_bucket,
        Key='multipartfile.txt',
        UploadId=uploadid,
        PartNumber=2,
        Body='B'*1024*1024*10
    )

    print "List Upload Parts"
    response = client.list_parts(
        Bucket=test_bucket,
        Key='multipartfile.txt',
        UploadId=uploadid
    )
    lst = response['Part']

    print "Test Complete MultipartUpload"
    response = client.complete_multipart_upload(
        Bucket=test_bucket,
        Key='multipartfile.txt',
        UploadId=uploadid,
        MultipartUpload={'Part': lst}
    )

if __name__ == "__main__":
    setUp()
    Test()
