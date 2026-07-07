export interface CommentApiResponse {
  comments_id: string;
  citizen_id: string;
  resource_id: string;
  parent_id: string | null;
  comments_text: string;
  comments_created_at: string;
}

export interface ResourceComment {
  id: string;
  authorId: string;
  resourceId: string;
  parentId: string | null;
  text: string;
  createdAt: string;
}

export interface CommentWritePayload {
  comments_text: string;
}