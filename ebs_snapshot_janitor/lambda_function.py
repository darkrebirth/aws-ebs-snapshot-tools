import boto3
import datetime
import json

def lambda_handler(event, context):
    ec = boto3.client('ec2')
    contextVariables = context.invoked_function_arn
    contextVariables = contextVariables.split(":")
    region = contextVariables[3]
    accountId = contextVariables[4]
    account_ids = [accountID]
    
    #grab a list of all snapshots
    snapshot_response = ec.describe_snapshots(OwnerIds=account_ids)
    snapshots=[]
    
    #create a list of tuples where each tuple contains the SnapshotId,StartTime,Description
    for s in snapshot_response['Snapshots']:
    	sid = s['SnapshotId']
    	stime = s['StartTime']
    	sdesc = s['Description']
    	snapshots.append((sid,stime,sdesc))
    
    #set the datetime for 30 days ago
    weekAgo = datetime.date.today() - datetime.timedelta(days=30)
    
    filteredList=[]
    deleteList=[]
    for s in snapshots:
    #Only delete EBS snapshots created by backup tool
    	if "EBS Snapshot" in s[2]:
    		filteredList.append(s)
    
    #Delete any snapshot older than 30 days
    for s in filteredList:
    	snapTime = s[1].date()
    	if snapTime < weekAgo:
    		deleteList.append(s)
    		ec.delete_snapshot(SnapshotId=s[0])