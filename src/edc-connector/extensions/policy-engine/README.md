<!--
  Copyright (c) 2024 Tecnalia, Basque Research & Technology Alliance (BRTA)
  
  Permission is hereby granted, free of charge, to any person obtaining a copy of
  this software and associated documentation files (the "Software"), to deal in
  the Software without restriction, including without limitation the rights to
  use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
  the Software, and to permit persons to whom the Software is furnished to do so,
  subject to the following conditions:
  
  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.
  
  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
  FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
  IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
  CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
  
  SPDX-License-Identifier: MIT
-->

# Policy engine extension

## DESCRIPTION
This project is intended to provide the **data policy usage definition and enforcement within the EDC connector**

The module is not accesible from the other modules directly.

It contains the code of the EDC policy extension which implements the policy engine for the following policies:
  - Time Interval Usage: allows data usage for an specific time interval´

```Example
{ 
  "@context":{ 
    "@vocab": "https://w3id.org/edc/v0.0.1/ns/" 
  }, 
  "@id":"aPolicyTimeInterval", 
  "@type":"edc:PolicyDefinition", 
  "policy": { 
     "@context": "http://www.w3.org/ns/odrl.jsonld", 
     "@type": "Set", 
     "permission": [ 
       { 
         "action": "use", 
         "constraint": [ 
           { 
             "@type": "AtomicConstraint", 
             "leftOperand": "https://w3id.org/edc/v0.0.1/ns/timeInterval", 
             "rightOperand":{ 
                "@type":"xsd:date", 
                "@value":"2022-12-31T23:00:00.000Z" 
             }, 
             "operator": { 
               "@id": "odrl:gteq" 
             } 
           }, 
           { 
             "@type": "AtomicConstraint", 
             "leftOperand": "https://w3id.org/edc/v0.0.1/ns/timeInterval", 
             "rightOperand":{ 
                "@type":"xsd:date", 
                "@value":"2024-09-30T23:00:00.000Z" 
             }, 
             "operator": { 
               "@id": "odrl:lteq" 
             } 
           } 
         ] 
       } 
     ], 
     "prohibition": [], 
     "obligation": [] 
} 
} 
```
 
   - Location Usage: allows data usage for a specific location

Example: 
```
{ 
  "@context":{ 
    "@vocab": "https://w3id.org/edc/v0.0.1/ns/" 
  }, 
  "@id":"aPolicyRegion", 
  "@type":"edc:PolicyDefinition", 
  "policy": { 
     "@context": "http://www.w3.org/ns/odrl.jsonld", 
     "@type": "Set", 
      "permission": [ 
           { 
               "action": "use", 
               "constraint": { 
                   "@type": "AtomicConstraint", 
                   "leftOperand": "https://w3id.org/edc/v0.0.1/ns/regionLocation", 
                   "operator": "odrl:eq", 
                   "rightOperand": "eu" 
               } 
           } 
       ] 
  } 
} 
```
  - Purpose Usage: allows data usage for specific purposes
Example:
```
{ 
   "@context":{ 
   "@vocab": "https://w3id.org/edc/v0.0.1/ns/" 
  }, 
 "@id":policy_id, 
 "@type":"edc:PolicyDefinition", 
  "policy": { 
    "@context": "http://www.w3.org/ns/odrl.jsonld", 
    "@type": "Set", 
     "permission": [ 
           { 
              "action": "use", 
              "constraint": { 
                  "@type": "AtomicConstraint", 
                  "odrl:leftOperand": "https://w3id.org/edc/v0.0.1/ns/purpose", 
                   "rightOperand": { 
                      "@type": "xsd:string", 
                      "@value": marketing 
                   }, 
                  "operator": { 
                      "@id":"odrl:eq" 
                   } 
               } 
           } 
       ] 
   } 
  } 
```

  



## INSTALLATION & REQUIREMENTS

The execution of the policy engine is integrated in the Eclipse Data Space connector as an extension.

This is the list or requirements and preconditions needed to execute the policy engine.

1. EDC connector installed
2. Keycloak installed




3. EDC configured in keycloak

For the last two policies we have included a claim in the Identity provider/Keycloak for the connector registered as a client:

  The next figure correspond with a "consumer-connector" client created at Keycloak:

  ![policy-engine-extension](doc/figures/consumer_connector_client.png)

  Once client is created you must go to "Client scopes" tab and click on "consumer-connector-dedicated" link

  ![policy-engine-extension](doc/figures/consumer_connector_client_client_scope.png)

  Click on "Add Mapper" button and select "By configuration" option:
  
  ![policy-engine-extension](doc/figures/create_claim_by_default.png)
  
  Create two "Hardcoded Claim" claims:

  ![policy-engine-extension](doc/figures/create_claim_harcoded.png)

And fill the information for purpose and location claims:

  Location claim:
  ![policy-engine-extension](doc/figures/keycloak_location_claim.PNG)

  Pursose claim:
  
  ![policy-engine-extension](doc/figures/keycloak_purpose_claim.PNG)

The result is:
![policy-engine-extension](doc/figures/keycloak_claim1.PNG)

4. EDC Asset model in the EDC linked with the ODRL policy (this is done in the contract definition)
   - 4.1.- Create asset
   - 4.2.- Create policy (N-times, location, purpose policy)
   - 4.3.- Create contract definition --> Link asset to policy
   - 4.4.- Negociate contract: in this steps is where the enforcement of the policies starts working, if the policy defined in the contract definition it is the right one the data transfer will be successful.

## USAGE

1. build.gradle.kts
Include these line in build.gradle.kts file:
   - implementation(libs.edc.contract.spi)
   - implementation(libs.edc.policy.engine.spi)

2.- Add an entry at "org.eclipse.edc.spi.system.ServiceExtension" file

![policy-engine-extension](doc/figures/service_extension.png)

## ROADMAP

Future versions of this project has to resolve the following points


## License
MIT