#!/usr/bin/env python3
import os
import yaml


kubeconf_template = """
  apiVersion: v1
  clusters:
  - cluster:
      server: https://KUBE_SERVER
    name: KUBE_SERVER_DASHIFY
  contexts:
  - context:
      cluster: KUBE_SERVER_DASHIFY
      namespace: NAMESPACE
      user: system:serviceaccount:NAMESPACE:SA_NAME/KUBE_SERVER_DASHIFY
    name: NAMESPACE/KUBE_SERVER_DASHIFY/system:serviceaccount:NAMESPACE:SA_NAME
  current-context: NAMESPACE/KUBE_SERVER_DASHIFY/system:serviceaccount:NAMESPACE:SA_NAME
  kind: Config
  preferences: {}
  users:
  - name: system:serviceaccount:NAMESPACE:SA_NAME/KUBE_SERVER_DASHIFY
    user:
      token: KUBE_TOKEN
"""

KUBE_SERVER = os.getenv('KUBE_SERVER')
KUBE_TOKEN = os.getenv('KUBE_TOKEN')
CONTEXT = os.getenv('CONTEXT') or 'dummyapp'
ENVIRONMENT = os.getenv('ENVIRONMENT') or 'production'
KUBECONF_EXT = os.getenv('KUBECONFVER')
SA_NAME = os.getenv('SA_NAME') or 'deploybot'
KUBEHOME = os.getenv('KUBEHOME') or '/home/invalid/.kube'

NAMESPACE = os.getenv('NAMESPACE') or CONTEXT + '-' + ENVIRONMENT
KUBE_SERVER_DASHED = str(KUBE_SERVER).replace(".", "-").replace("https://","")

kubeconf = yaml.safe_load(kubeconf_template)
clusters = kubeconf['clusters']
clusters[0]['name'] = KUBE_SERVER_DASHED
clusters[0]['cluster']['server'] = KUBE_SERVER

contexts = kubeconf['contexts']
context_name_fmt = "{}/{}/system:serviceaccount:{}:{}"
contexts[0]['name'] = context_name_fmt.format(NAMESPACE, KUBE_SERVER_DASHED,
                                              NAMESPACE, SA_NAME)
contexts[0]['context']['cluster'] = KUBE_SERVER_DASHED
contexts[0]['context']['namespace'] = NAMESPACE
context_user_fmt = "system:serviceaccount:{}:{}/{}"
contexts[0]['context']['user'] = context_user_fmt.format(NAMESPACE, SA_NAME,
                                                         KUBE_SERVER_DASHED)

users = kubeconf['users']
user_name_fmt = "system:serviceaccount:{}:{}/{}"
users[0]['name'] = user_name_fmt.format(NAMESPACE, SA_NAME, KUBE_SERVER_DASHED)
users[0]['user']['token'] = KUBE_TOKEN

kubeconf['current-context'] = context_name_fmt.format(NAMESPACE,
                                                      KUBE_SERVER_DASHED,
                                                      NAMESPACE, SA_NAME)

if KUBECONF_EXT:
  outfile = "{}/cfg-{}-{}".format(KUBEHOME, CONTEXT, KUBECONF_EXT)
else:
  outfile = "{}/cfg-{}-new".format(KUBEHOME, CONTEXT)

print("Writing kube config out to \"{}\"...".format(outfile))
with open(outfile, 'wb') as stream:
  try:
    yaml.safe_dump(kubeconf, stream, default_flow_style=False,
                   explicit_start=True, allow_unicode=True, encoding='utf-8')
    print("Great success!")
  except yaml.YAMLError as err:
    print(err)
