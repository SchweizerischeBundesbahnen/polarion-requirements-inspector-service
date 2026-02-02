# Polarion Requirements Inspector Service
Service providing REST API to use Polarion Requirements Inspector functionality

## Build Docker image

```bash
  docker build \
    --build-arg APP_IMAGE_VERSION=0.0.0-dev \
    --file Dockerfile \
    --tag polarion-requirements-inspector-service:0.0.0-dev \
    .
```

## Start Docker container

```bash
  docker run --detach \
    --init \
    --publish 9080:9080 \
    --name polarion-requirements-inspector-service \
    polarion-requirements-inspector-service:0.0.0-dev
```

## Stop Docker container

```bash
  docker container stop polarion-requirements-inspector-service
```

### Access service
Polarion Requirements Inspector Service provides the following endpoints:

<details>
  <summary>
    <code>GET</code> <code>/version</code>
  </summary>

##### Responses

> | HTTP code | Content-Type       | Response                                                                                                          |
> |-----------|--------------------|-------------------------------------------------------------------------------------------------------------------|
> | `200`     | `application/json` | `{"python":"3.12.3","polarion_requirements_inspector":"4.0.0","polarion_requirements_inspector_service":"2.0.1"}` |

##### Example cURL

> ```bash
>  curl -X GET -H "Content-Type: application/json" http://localhost:9081/version
> ```

</details>

#### Analyze work items

<details>
  <summary>
    <code>POST</code> <code>/analyze/workitems</code>
  </summary>

##### Body

> | Type     | Data type      | Description                                                          |
> |----------|----------------|----------------------------------------------------------------------|
> | Required | JSON string    | JSON encoding of type list[WorkItem]                                 |

##### Responses

> | HTTP code | Content-Type      | Response                                          |
> |-----------|-------------------|---------------------------------------------------|
> | `200`     | `application/json`| JSON file                                         |
> | `400`     | `plain/text`      | Bad Request: JSON Decode Error                    |
> | `413`     | `plain/text`      | Request Entity Too Large: JSON Body too large     |
> | `500`     | `plain/text`      | Internal Server Error: Unknown Error              |

##### Example cURL

> ```bash
>   curl -X POST \
>   -H "Content-Type: application/json" \
>   -H "Accept: application/json" \
>   --data '[{"title":"example","description":"example","language":"en"}]' \
>   http://localhost:9081/inspect/workitems
> ```
</details>

## Testing Docker image

```bash
docker build -t polarion-requirements-inspector-service:local .
container-structure-test test --image polarion-requirements-inspector-service:local --config .config/container-structure-test.yaml
```
