export interface AdminUser {
  user_id:        string;
  user_fname:     string;
  user_lname:     string;
  user_mail:      string;
  is_super_admin: boolean;
}

export interface AdminLoginResponse {
  access:  string;
  refresh: string;
  user:    AdminUser;
}

export interface AdminRecord {
  admin_id:            string;
  user_fname:          string;
  user_lname:          string;
  user_mail:           string;
  is_active:           boolean;
  admin_is_super_admin: boolean;
  admin_created_at:    string;
}
