export interface Category {
  category_id: string;
  label: string;
}

export interface Relation {
  relation_id: string;
  label: string;
}

export type ResourceLabel =
  | 'reading_sheet' | 'games' | 'videos' | 'pdf'
  | 'activity' | 'article' | 'challenge_card' | 'exercise';

export const RESOURCE_LABEL_DISPLAY: Record<ResourceLabel, string> = {
  reading_sheet:  'Fiche de lecture',
  games:          'Jeu',
  videos:         'Vidéo',
  pdf:            'PDF',
  activity:       'Activité',
  article:        'Article',
  challenge_card: 'Carte défi',
  exercise:       'Exercice',
};

export interface ResourceAuthor {
  user_id:    string;
  user_fname: string;
  user_lname: string;
}

export interface ResourceReadingSheet {
  book_title:   string;
  book_author?: string;
  summary?:     string;
}

export interface ResourceGames {
  game_url?:          string;
  game_platform?:     string;
  game_instructions?: string;
}

export interface ResourceVideos {
  video_url:       string;
  video_duration:  number;
  video_platform?: string;
}

export interface ResourcePDF {
  pdf_url:         string;
  pdf_publisher?:  string;
  pdf_page_count?: number;
  pdf_size?:       number;
}

export interface ResourceActivity {
  activity_instructions?:       string;
  activity_duration?:           number;
  activity_required_materials?: string;
}

export interface ResourceArticle {
  article_url:        string;
  article_publisher?: string;
}

export interface ResourceChallengeCard {
  challenge_card_duration?: number;
}

export interface ResourceExercise {
  exercise_instructions?: string;
  exercise_duration?:     number;
}

export interface Resource {
  resource_id:           string;
  resource_author:       ResourceAuthor;
  resource_created_at:   string;
  resource_last_modif:   string;
  resource_is_visible:   boolean;
  resource_title:        string;
  resource_description?: string;
  resource_label?:       ResourceLabel;
  categories:            Category[];
  relations:             Relation[];
  reading_sheet?:        ResourceReadingSheet;
  games?:                ResourceGames;
  videos?:               ResourceVideos;
  pdf?:                  ResourcePDF;
  activity?:             ResourceActivity;
  article?:              ResourceArticle;
  challenge_card?:       ResourceChallengeCard;
  exercise?:             ResourceExercise;
  likes_count?:          number;
  favori_count?:         number;
}

export interface PagedResponse<T> {
  count:     number;
  next?:     string | null;
  previous?: string | null;
  results:   T[];
}

export interface ResourceFilters {
  category?: string;
  label?:    string;
  relation?: string;
  q?:        string;
  ordering?: string;
}
