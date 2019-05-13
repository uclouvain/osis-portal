# openapi_client.DefaultApi

All URIs are relative to *https://dev.osis.uclouvain.be/api/v1/continuing_education*

Method | HTTP request | Description
------------- | ------------- | -------------
[**admissions_post**](DefaultApi.md#admissions_post) | **POST** /admissions | 
[**admissions_uuid_delete**](DefaultApi.md#admissions_uuid_delete) | **DELETE** /admissions/{uuid} | 
[**admissions_uuid_get**](DefaultApi.md#admissions_uuid_get) | **GET** /admissions/{uuid} | 
[**admissions_uuid_patch**](DefaultApi.md#admissions_uuid_patch) | **PATCH** /admissions/{uuid} | 
[**admissions_uuid_put**](DefaultApi.md#admissions_uuid_put) | **PUT** /admissions/{uuid} | 
[**persons_details_get**](DefaultApi.md#persons_details_get) | **GET** /persons/details | 


# **admissions_post**
> admissions_post(admission_post_put_patch)



Create a new admission.

### Example

* Api Key Authentication (Token): 
```python
from __future__ import print_function
import time
import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: Token
configuration = openapi_client.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = openapi_client.DefaultApi(openapi_client.ApiClient(configuration))
admission_post_put_patch = openapi_client.AdmissionPostPutPatch() # AdmissionPostPutPatch | 

try:
    api_instance.admissions_post(admission_post_put_patch)
except ApiException as e:
    print("Exception when calling DefaultApi->admissions_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **admission_post_put_patch** | [**AdmissionPostPutPatch**](AdmissionPostPutPatch.md)|  | 

### Return type

void (empty response body)

### Authorization

[Token](../README.md#Token)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **admissions_uuid_delete**
> admissions_uuid_delete(uuid)



Delete an existing admission

### Example

* Api Key Authentication (Token): 
```python
from __future__ import print_function
import time
import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: Token
configuration = openapi_client.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = openapi_client.DefaultApi(openapi_client.ApiClient(configuration))
uuid = 'uuid_example' # str | The UUID of the admission

try:
    api_instance.admissions_uuid_delete(uuid)
except ApiException as e:
    print("Exception when calling DefaultApi->admissions_uuid_delete: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | [**str**](.md)| The UUID of the admission | 

### Return type

void (empty response body)

### Authorization

[Token](../README.md#Token)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **admissions_uuid_get**
> AdmissionGet admissions_uuid_get(uuid)



Obtain information about a specific admission

### Example

* Api Key Authentication (Token): 
```python
from __future__ import print_function
import time
import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: Token
configuration = openapi_client.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = openapi_client.DefaultApi(openapi_client.ApiClient(configuration))
uuid = 'uuid_example' # str | The UUID of the admission

try:
    api_response = api_instance.admissions_uuid_get(uuid)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->admissions_uuid_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | [**str**](.md)| The UUID of the admission | 

### Return type

[**AdmissionGet**](AdmissionGet.md)

### Authorization

[Token](../README.md#Token)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **admissions_uuid_patch**
> admissions_uuid_patch(uuid, admission_post_put_patch)



Edit a part of an existing admission

### Example

* Api Key Authentication (Token): 
```python
from __future__ import print_function
import time
import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: Token
configuration = openapi_client.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = openapi_client.DefaultApi(openapi_client.ApiClient(configuration))
uuid = 'uuid_example' # str | The UUID of the admission
admission_post_put_patch = openapi_client.AdmissionPostPutPatch() # AdmissionPostPutPatch | 

try:
    api_instance.admissions_uuid_patch(uuid, admission_post_put_patch)
except ApiException as e:
    print("Exception when calling DefaultApi->admissions_uuid_patch: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | [**str**](.md)| The UUID of the admission | 
 **admission_post_put_patch** | [**AdmissionPostPutPatch**](AdmissionPostPutPatch.md)|  | 

### Return type

void (empty response body)

### Authorization

[Token](../README.md#Token)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **admissions_uuid_put**
> admissions_uuid_put(uuid, admission_post_put_patch)



Edit an existing admission

### Example

* Api Key Authentication (Token): 
```python
from __future__ import print_function
import time
import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: Token
configuration = openapi_client.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = openapi_client.DefaultApi(openapi_client.ApiClient(configuration))
uuid = 'uuid_example' # str | The UUID of the admission
admission_post_put_patch = openapi_client.AdmissionPostPutPatch() # AdmissionPostPutPatch | 

try:
    api_instance.admissions_uuid_put(uuid, admission_post_put_patch)
except ApiException as e:
    print("Exception when calling DefaultApi->admissions_uuid_put: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | [**str**](.md)| The UUID of the admission | 
 **admission_post_put_patch** | [**AdmissionPostPutPatch**](AdmissionPostPutPatch.md)|  | 

### Return type

void (empty response body)

### Authorization

[Token](../README.md#Token)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **persons_details_get**
> InlineResponse200 persons_details_get()



Obtain uuid of the connected person (participant)

### Example

* Api Key Authentication (Token): 
```python
from __future__ import print_function
import time
import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: Token
configuration = openapi_client.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = openapi_client.DefaultApi(openapi_client.ApiClient(configuration))

try:
    api_response = api_instance.persons_details_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->persons_details_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**InlineResponse200**](InlineResponse200.md)

### Authorization

[Token](../README.md#Token)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

