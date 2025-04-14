
export interface OAuth2AssetProps {
    "oauth2:tokenUrl": string;
    "oauth2:clientId": string;
    "oauth2:clientSecret": string;
    "oauth2:grantType": string;
    "oauth2:scope"?: string;
    // in case of password grant-type
    "oauth2:username"?: string;
    "oauth2:password"?: string;
}