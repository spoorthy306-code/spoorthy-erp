export interface User {
  id: string | number;
  username: string;
  name?: string;
  email?: string;
  role: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type?: string;
  user?: User;
}
