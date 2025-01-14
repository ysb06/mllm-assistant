export interface IEventElement {
    data: any,
    event: string,
    metadata: any,
    name: string,
    parent_ids: string[],
    run_id: string,
    tags: string[]
}

export interface IChatElement {
    role: string,
    content: string
}