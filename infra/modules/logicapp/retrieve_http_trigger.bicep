param logicAppName string
param triggerName string

resource logicApp 'Microsoft.Logic/workflows@2019-05-01' existing = {
  name: logicAppName
}
resource trigger 'microsoft.logic/workflows/triggers@2019-05-01' existing = {
  name: triggerName
  parent: logicApp
}

#disable-next-line outputs-should-not-contain-secrets
output url string = trigger.listCallbackUrl().value
