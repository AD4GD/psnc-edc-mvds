
export enum ParticipantStatusType {
    ONBOARDING_INITIATED = 0, // onboarding request received
    AUTHORIZING = 100, // verifying participants credentials
    AUTHORIZED = 200, // participant is authorized
    ONBOARDED = 300, // participant is fully onboarded
    DENIED = 400, // participant onboarding request denied
    FAILED = -1, // participant onboarding failed
    DELETED = -100,
}
