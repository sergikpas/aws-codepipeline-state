import sys
import os
import argparse
import boto3
import json
import time

parser = argparse.ArgumentParser(prog='translate')
parser.add_argument('--profile',
                    help='AWS profile that will be used for translation')
parser.add_argument('--name',
                    help='AWS pipeline name, that should be monitored')
parser.add_argument('--timeout',
                    type=int,
                    help='How long application can wait for result about CodePipeline state',
                    default=30)

args = vars(parser.parse_args(sys.argv[1:]))

session = boto3.Session(profile_name=args['profile'])
codepipeline = session.client('codepipeline')
print('run test')

finished = False
start = time.time()
execution = 0

print('Time out after %s ' % args['timeout'])
while finished == False and execution < args['timeout']:
    try:
        codepipeline_state = codepipeline.get_pipeline_state(
            name=args['name'])

        if 'stageStates' not in codepipeline_state:
            print('Failed! Can\'t find Stages!')

        failed = False
        progress = None
        for state in codepipeline_state['stageStates']:
            print('Stage: [%s] - %s' %
                  (state['stageName'], state['latestExecution']['status']))
            if state['latestExecution']['status'] in ('Succeeded', 'Failed'):
                if progress == None:
                    progress = False
                if state['latestExecution']['status'] == 'Failed':
                    failed = True
            elif state['latestExecution']['status'] == 'InProgress':
                progress = True

        if progress == False:
            finished = True
    except:
        print(sys.exc_info(), "occured.")
        failed = True
        finished = True
    execution = int(time.time() - start)

    time.sleep(1)

print('Application executed %s secs' % (execution,))

if finished == False:
    print('[FAILED] - CodePipeline execution take too long time. Application timed out...')
    quit(1)

if failed == False:
    print('[OK] - Application successfully deployed')
    sys.exit(0)
else:
    print('[FAILED] - Failed deploy application')
    sys.exit(1)
