export type InteractionCollection = 'likes' | 'favoris' | 'bookmarks' | 'exploited';
export type InteractionToggleKind = 'like' | 'favorite' | 'bookmark' | 'exploited';
export type InteractionCountMap = Partial<Record<InteractionToggleKind, number>>;

export interface InteractionApiResponse {
  citizen_id?:    string;
  resource_id:    string;
  resource_title?: string;
  is_liked:       boolean;
  is_favorise:    boolean;
  is_bookmark:    boolean;
  is_exploited:   boolean;
}

export interface InteractionWritePayload {
  is_liked?: boolean;
  is_favorise?: boolean;
  is_bookmark?: boolean;
  is_exploited?: boolean;
}

export interface ResourceInteractionState {
  citizenId:     string | null;
  resourceId:    string;
  resourceTitle: string;
  liked:         boolean;
  favorite:      boolean;
  bookmarked:    boolean;
  exploited:     boolean;
}

export interface InteractionSummaryApiResponse {
  likes: number;
  favoris: number;
  bookmarks: number;
  exploited: number;
}

export interface InteractionSummary {
  likes: number;
  favorites: number;
  bookmarks: number;
  exploited: number;
  total: number;
}