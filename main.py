
import csv
import re

BUCKETS = []
KEYS_THRESHOLD = 0.7

def similar(value, bucket):
    common_keys = value.keys() & bucket.keys()
    return len(common_keys)/len(value.keys()) > KEYS_THRESHOLD

def clean(value):
    """
    variable fields:
    - name
    - date time
    - expanded date; eg: 22 december, 2016
    - account number
    - transaction id
    - amounts
    - FY or AY year eg: 17-18 or 2017-18 or 2017-2018
    - PAN number - eg: ABCDS1234Y or *******34Y
    - percents 22.3%
    - random refrence nos, cheque nos, etc
    """
    patterns = [
        re.compile(r"\d{2,4}[-/](\d{1,2}|[a-z|A-Z]{3})[-/]\d{1,4}"),  # date pattern
        re.compile(r"\d{2}:\d{2}:\d{2}"),  # time pattern
        re.compile(r"[Xx\*]+\d{3,4}"),  # account number parrern
        re.compile(r"(INR|RS)\.?\s?(\d+(\,?|\.)+)+\d+", re.I),  # amounts pattern; ex: "INR 201.23"
        re.compile(r"[a-zA-z]{5}\d{4}[a-zA-Z]|[Xx\*]{7}\d{2}[a-zA-Z]", re.I),  # pan number
        re.compile(r"[a-zA-Z]{3}\s+\d{2},+\s+\d{4}", re.I),  # special date pattern;eg: Mar 17, 2017
        re.compile(r"\d{5,}", re.I),  # random cheque, ref nos
    ]
    for pattern in patterns:
        value = re.sub(pattern, '', value)
    return value.strip()

def check(value):
    data = value.get('map')
    if len(BUCKETS) == 0:
        BUCKETS.append(value)
    else:
        # check if the 2 buckets are similar
        for bucket in BUCKETS:
            bucket_hmap = bucket.get('map')
            if similar(data, bucket_hmap):
                bucket.get('raw').extend(value.get('raw'))
                for key in data.keys():
                    if key in bucket_hmap.keys():
                        bucket_hmap[key] += 1
                    else:
                        bucket_hmap.update({key: 0})
                return
        BUCKETS.append(value)

raw_data = []
print('+'*10,'Reading file','+'*10)
with open('test.csv', 'r', encoding="utf-8", errors='ignore') as csvfile:
    for row in csv.reader(csvfile):
        raw_data.append(row[0])

total = 0
print('+'*10,'Total rows - {}'.format(len(raw_data)),'+'*10)
print('+'*10,'Cleaning/mapping data','+'*10)
for line in raw_data:
    words = clean(line).split(' ')
    # total += len(words)
    words = [word.strip() for word in words]
    hmap = dict(zip(words, [0]*len(words)))
    bucket = {
        'map': hmap,
        'raw': [clean(line)]
    }
    check(bucket)

# print(total/len(raw_data))
x=0
print('+'*10,'Total buckets - {}'.format(len(BUCKETS)),'+'*10)
print('+'*10,'Printing data','+'*10)
for bucket in sorted(BUCKETS, key=lambda k: len(k['raw'])):
    x = x+1 if len(bucket['raw']) < 5 else x+0
    print('-'*10)
    print(len(bucket['raw']))
    print('\n'.join(bucket['raw']))
    print('-'*10)

print('+'*10,'< 5 sms in bucket count - {}'.format(x),'+'*10)