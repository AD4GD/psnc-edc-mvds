import { ParticipantStatusType } from "../enums/participant-status-type.enum";

export interface Participant {
    did: string,
    protocolUrl: string,
    status: ParticipantStatusType,
    claims: Map<string, string> | undefined,
}
