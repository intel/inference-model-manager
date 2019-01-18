# Inference Model Manager for Kubernetes

*Inference Model Manager for Kubernetes* is an open source SW platform intended to provide convenient solution for 
hosting, management and scaling inference processing endpoints exposed over gRPC protocol.

It is built on top of Kubernetes and integrates with Tensorflow Serving for exposing the inference endpoints.

It is intended for organizations who dynamically deploy and scale inference endpoints.
- Users are organized into tenants
- Multiple tenants are supported with “soft” isolation between tenants	

Inference Model Manager for Kubernetes includes a custom REST API which simplifies the configuration and management of hosted inference services.
Inference Model Manager integrates with Minio or other S3 compatible components used for storage of the AI models.

Inference Model Manager for Kubernetes conjoins inference services scalability and easy management with 
security features like:
- limiting access to inference endpoints to authorized clients only
- preventing unauthorized access to management API
- limiting access to tenant data based on group membership information from external identity provider.

[Installation quicksheet (beta)](docs/exampleinstallation.md)

[Architecture overview](docs/architecture.md)

[Prerequisites and requirements](docs/prerequisites.md)

[Building platform components](docs/building.md)

[Deployment guide](docs/deployment.md)

[Platform admin guide](docs/platform_admin_guide.md)

[Platform user guide](docs/platform_user_guide.md)

[Example grpc client](examples/grpc_client)

[Security recommendation for Kubernetes](docs/security_recommendations.md)

[Troubleshooting](docs/troubleshooting.md)

[Serving templates](docs/serving_templates.md)
