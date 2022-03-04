import ray
from ray import serve


@serve.deployment
class Deployment:
    def method1(self, arg):
        return f"Method1: {arg}"

    def __call__(self, arg):
        return f"__call__: {arg}"

Deployment.deploy()

handle = Deployment.get_handle()
ray.get(handle.remote("hi")) # Defaults to calling the __call__ method.
ray.get(handle.method1.remote("hi")) # Call a different method.