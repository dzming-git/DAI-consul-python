import requests
import json
from .service_info import ServiceInfo
from urllib.parse import quote
from typing import Union

class ConsulClient:
    def __init__(self):
        self.consul_ip = "127.0.0.1"
        self.consul_port = "8500"

    def register_service(self, service_info: ServiceInfo):
        url = f"http://{self.consul_ip}:{self.consul_port}/v1/agent/service/register"
        service_info_dict = {
            "Id": service_info.service_id,
            "Name": service_info.service_name,
            "Address": service_info.service_ip,
            "Port": int(service_info.service_port),
            "Tags": service_info.service_tags
        }
        
        if not service_info.service_check.url:
            service_info.service_check.url = f"{service_info.service_ip}:{service_info.service_port}"

        service_check_info = {
            service_info.service_check.protocol: service_info.service_check.url,
            "Interval": f"{service_info.service_check.interval_ms}ms",
            "DeregisterCriticalServiceAfter": f"{service_info.service_check.interval_ms * 3}ms"
        }

        service_info_dict["Check"] = service_check_info
        payload = json.dumps(service_info_dict)

        headers = {
            "Content-Type": "application/json"
        }

        response = requests.put(url, data=payload, headers=headers)
        print(f"PUT {url}")
        print(response.text)
        return response.ok
    
    def get_service_address(self, service_name):
        encoded_service_name = quote(service_name)
        url = f"http://{self.consul_ip}:{self.consul_port}/v1/catalog/service/{encoded_service_name}"
        response = requests.get(url)
        if response.ok:
            services = response.json()
            if services:
                # Assuming there may be multiple instances of the service, we return the first one
                service = services[0]
                address = service["ServiceAddress"]
                port = service["ServicePort"]
                return address, str(port)
        return '', ''