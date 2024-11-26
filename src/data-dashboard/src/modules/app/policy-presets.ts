import { PolicyPresetType } from "../edc-demo/models/policy-preset-type"

export const LOCATION_PRESET: PolicyPresetType = {
    id: 'location',
    name: 'Location',
    odrlJsonString: 
    `
    { 
        "action": "use", 
        "constraint": { 
            "@type": "AtomicConstraint", 
            "leftOperand": "https://w3id.org/edc/v0.0.1/ns/regionLocation", 
            "operator": "odrl:eq", 
            "rightOperand": "{{location}}" 
        } 
    }
    `
}

export const PURPOSE_PRESET: PolicyPresetType = {
    id: 'purpose',
    name: 'Purpose',
    odrlJsonString:
    `
    { 
        "action": "use", 
        "constraint": { 
            "@type": "AtomicConstraint", 
            "odrl:leftOperand": "https://w3id.org/edc/v0.0.1/ns/purpose", 
            "rightOperand": { 
                "@type": "xsd:string", 
                "@value": "{{purpose}}" 
            }, 
            "operator": { 
                "@id":"odrl:eq" 
            } 
        } 
    } 
    `
}

// Time format is yyyy-mm-ddThh:mm:sssZ (UTC)
export const TIME_INTERVAL_PRESET: PolicyPresetType = {
    id: 'timeinterval',
    name: 'Time interval',
    odrlJsonString:    
    `
    {
        "action": "use",
        "constraint": [
            {
                "@type": "AtomicConstraint",
                "leftOperand": "https://w3id.org/edc/v0.0.1/ns/timeInterval",
                "rightOperand": {
                    "@type": "xsd:date",
                    "@value": "{{timeFrom}}"
                },
                "operator": {
                    "@id": "odrl:gteq"
                }
            },
            {
                "@type": "AtomicConstraint",
                "leftOperand": "https://w3id.org/edc/v0.0.1/ns/timeInterval",
                "rightOperand": {
                    "@type": "xsd:date",
                    "@value": "{{timeTo}}"
                },
                "operator": {
                    "@id": "odrl:lteq"
                }
            }
        ]
    }
    `
}

export const CUSTOM_PRESET: PolicyPresetType = {
    id: 'custom',
    name: 'Custom',
    odrlJsonString: "{}"
}