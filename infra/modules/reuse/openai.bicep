param azureOpenaiResourceName string

resource openai 'Microsoft.CognitiveServices/accounts@2024-10-01' existing = {
  name: azureOpenaiResourceName
}

output openaiId string = openai.id
output openaiEndpoint string = openai.properties.endpoint
