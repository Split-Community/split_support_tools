#!/bin/sh
cd /home/ec2-user/gainsight_sync/split_support_tools/gainsight_segments_sync
/usr/bin/python3 gs_sg_sync.py > gainsight_sync_output.txt 2>&1