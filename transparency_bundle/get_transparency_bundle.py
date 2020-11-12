import requests
import datetime
import os
from zipfile import ZipFile 
from dotenv import load_dotenv

load_dotenv()

from google.cloud import storage

GCS_BUCKET_PREFIX = "google_political_ads_transparency_bundles"
def upload_csv_to_gcs(destination_blob_name, file_as_string):
  storage_client = storage.Client()
  bucket = storage_client.get_bucket(bucket_name)
  blob = bucket.blob(os.path.join(os.environ.get("GCS_BUCKET"), GCS_BUCKET_PREFIX, destination_blob_name))
  blob.upload_from_string(file_as_string)


def write_current_bundle_to_disk(dest, zip_file, update_date):
    filename = "google-political-ads-transparency-bundle-{}.zip".format(update_date)
    dest = os.path.join(dest, filename)
    with open(dest, 'wb') as f:
        f.write(zip_file.read())

def write_advertiser_stats_to_disk(dest, csv, update_date):
    filename = "google-political-ads-advertiser-stats-{}.csv".format(update_date)
    dest = os.path.join(dest, filename)
    with open(dest, 'wb') as f:
        f.write(csv)


def get_current_bundle():
    """ downloads the zip file from the Google Political Transpareny Report

        returns a file-like
    """
    if False:
        BUNDLE_URL = "https://storage.googleapis.com/transparencyreport/google-political-ads-transparency-bundle.zip"
        resp = requests.get(BUNDLE_URL)
        return resp.content()
    else:
        return open(os.path.join(os.path.dirname(__file__), '..', '..', 'youtubeadlibrary', 'google-political-ads-transparency-bundle (6).zip'), 'rb')


def get_zip_file_by_name(bundle_filelike, filename):
    with ZipFile(bundle_filelike, 'r') as zip:
        return zip.read("google-political-ads-transparency-bundle/{}".format(filename))

def get_bundle_date(bundle_filelike):
    data = get_zip_file_by_name(bundle_filelike, 'google-political-ads-updated.csv')
    updated_date = data.decode('utf-8').split("\n")[1]
    return updated_date


def get_advertiser_stats_csv(bundle_filelike):
    """
        the Google Political Transparency Bundle contains 9 CSVs:

         15K  README.txt
         10K  google-political-ads-advertiser-declared-stats.csv
         13M  google-political-ads-advertiser-geo-spend.csv
        749K  google-political-ads-advertiser-stats.csv
        7.8M  google-political-ads-advertiser-weekly-spend.csv
        148B  google-political-ads-campaign-targeting.csv
        639M  google-political-ads-creative-stats.csv
         59K  google-political-ads-geo-spend.csv
         10K  google-political-ads-top-keywords-history.csv
         36B  google-political-ads-updated.csv

        we don't want to save all of them, since they tend to be duplicative.
    """
    return get_zip_file_by_name(bundle_filelike, 'google-political-ads-advertiser-stats.csv')


def upload_advertiser_stats_from_bundle(zip_file):
    bundle_date = get_bundle_date(zip_file)
    advertiser_stats_csv = get_advertiser_stats_csv(zip_file)
    write_current_bundle_to_disk(local_dest_for_bundle, zip_file, bundle_date)
    write_advertiser_stats_to_disk(local_dest_for_bundle, advertiser_stats_csv, bundle_date)
    upload_csv_to_gcs("google-political-ads-advertiser-stats-{}.csv".format(update_date), advertiser_stats_csv)

def do_stuff(local_dest_for_bundle):
    with get_current_bundle() as zip_file:
        upload_advertiser_stats_from_bundle(zip_file)

if __name__ == "__main__":
    local_dest_for_bundle = os.path.join(os.path.dirname(__file__), '..', 'data')
    do_stuff(local_dest_for_bundle)