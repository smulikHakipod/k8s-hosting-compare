#!/usr/bin/python3
import os
import subprocess
import prometheus_client
import yaml
import time
from prometheus_client.exposition import push_to_gateway
import typing
import urllib.request
# run stress-ng command and send the yaml out.yaml to Prometheus using the prometheus-client library


def run_stress():
    # run stress-ng command
    subprocess.run(["stress-ng", "--cpu", "1", "--timeout", "60s", "--metrics", "--yaml", "/app/out.yaml"])
    # read yaml file
    with open('/app/out.yaml') as f:
        data = yaml.safe_load(f)

    print("Sending metrics to Prometheus Pushgateway")


    # Create a CollectorRegistry object
    registry = prometheus_client.CollectorRegistry()

    # Create gauges and register them in the registry
    gauges = [
        prometheus_client.Gauge(
            'bogo_ops_per_second_usr_sys_time',
            'Bogo operations per second (usr+sys time)',
        ),
        prometheus_client.Gauge(
            'bogo_ops_per_second_real_time',
            'Bogo operations per second (real time)',
        ),
        prometheus_client.Gauge(
            'wall_clock_time',
            'Wall clock time',
        ),
        prometheus_client.Gauge(
            'user_time',
            'User time',
        ),
        prometheus_client.Gauge(
            'system_time',
            'System time',
        ),
        prometheus_client.Gauge(
            'cpu_usage_per_instance',
            'CPU usage per instance',
        ),
        prometheus_client.Gauge(
            'max_rss',
            'Maximum resident set size (max RSS)',
        ),
    ]

    for gauge in gauges:
        registry.register(gauge)

    # Set the metric values
    gauges[0].set(data['metrics'][0]['bogo-ops-per-second-usr-sys-time'])
    gauges[1].set(data['metrics'][0]['bogo-ops-per-second-real-time'])
    gauges[2].set(data['metrics'][0]['wall-clock-time'])
    gauges[3].set(data['metrics'][0]['user-time'])
    gauges[4].set(data['metrics'][0]['system-time'])
    gauges[5].set(data['metrics'][0]['cpu-usage-per-instance'])
    gauges[6].set(data['metrics'][0]['max-rss'])

    # Send metrics to Prometheus Pushgateway
    prometheus_user = os.environ.get('PROMETHEUS_USER')
    prometheus_password = os.environ.get('PROMETHEUS_PASS')

    provider = os.environ.get('PROVIDER')

    if not provider:
        print('PROVIDER environment variable is not set')
        exit(1)

    # Construct the Prometheus Pushgateway URL
    prometheus_url = 'http://ppushgateway.yaronshani.me/'

    def handler(url, method, timeout, headers, data):
        import base64
        '''Handler that implements HTTP Basic Auth using environment variables 'PUSHGW_USERNAME' and 'PUSHGW_PASSWORD'.'''
        auth_value = "{0}:{1}".format(prometheus_user, prometheus_password)
        auth_header = b"Basic " + base64.b64encode(auth_value.encode('utf-8'))
        headers.append(['Authorization', auth_header])
        return prometheus_client.exposition.default_handler(url, method, timeout, headers, data)

    # Push metrics to Prometheus Pushgateway
    push_to_gateway(
        prometheus_url,
        job='stress-cpu',
        registry=registry,
        handler=handler,
        grouping_key={'instance': provider},
    )

    # Reset metric values
    for gauge in gauges:
        gauge.set(float('nan'))


# Run stress every 10 minutes
while True:
    run_stress()
    time.sleep(600)
