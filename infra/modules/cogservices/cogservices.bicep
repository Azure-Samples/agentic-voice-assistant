param location string
param resourceName string

resource cognitiveService 'Microsoft.CognitiveServices/accounts@2021-04-30' = {
  name: resourceName
  location: location
  kind: 'CognitiveServices'
  sku: {
    name: 'S0'
  }
  properties: {
    customSubDomainName: resourceName
  }
}

output cognitiveServiceId string = cognitiveService.id
output cognitiveServiceName string = cognitiveService.name
output cognitiveServiceEndpoint string = cognitiveService.properties.endpoint
output cognitiveServiceRegion string = cognitiveService.location
