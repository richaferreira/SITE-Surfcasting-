export type Beach = {
  id: number;
  name: string;
  slug: string;
  city: string;
  state: string;
  description: string | null;
  latitude: number;
  longitude: number;
  sea_bearing_deg: number;
  beach_profile: "TOMBO" | "INTERMEDIARIA" | "RASA" | "ABRIGADA";
  accessibility_summary: string | null;
  is_published?: boolean;
};

export type FishingPoint = {
  id: number;
  name: string;
  slug: string;
  point_type: "BURACO" | "COROA_AREIA" | "CANAL_RETORNO" | "ESTRUTURA" | "OUTRO";
  description: string | null;
  latitude: number;
  longitude: number;
  accessibility: "FACIL" | "MODERADA" | "DIFICIL" | "RESTRITA";
  access_notes: string | null;
  risk_notes: string | null;
  verified_at: string | null;
};

export type FishingScore = {
  score: number | null;
  label: string;
  calculated_at: string;
  conditions: {
    wind_speed_mps: number | null;
    wind_direction_deg: number | null;
    sea_bearing_deg: number;
    wind_is_offshore: boolean | null;
    tide_trend: string;
    wave_height_m: number | null;
    wave_period_s: number | null;
    water_temperature_c: number | null;
    pressure_hpa: number | null;
    moon_phase: string;
  };
  breakdown: Record<string, number>;
  reasons: string[];
  warnings: string[];
  data_quality: {
    is_sufficient: boolean;
    confidence_percentage: number;
    available_components: string[];
    missing_components: string[];
  };
  cached: boolean;
};

export type MarineForecastHour = {
  observed_at: string;
  wave_height_m: number | null;
  wave_period_s: number | null;
  water_temperature_c: number | null;
  wind_speed_mps: number | null;
  wind_direction_deg: number | null;
  pressure_hpa: number | null;
};

export type TideExtreme = {
  occurs_at: string;
  extreme_type: "high" | "low";
  height_m: number | null;
};

export type MarineForecast = {
  generated_at: string;
  source: string;
  hours: MarineForecastHour[];
  tides: TideExtreme[];
  warnings: string[];
  data_quality: {
    hours_requested: number;
    hours_returned: number;
    complete_hours: number;
    coverage_percentage: number;
  };
};

export type AcademyPostSummary = {
  id: number;
  title: string;
  slug: string;
  excerpt: string | null;
  content_type: "ARTIGO" | "TUTORIAL" | "VIDEO" | "EQUIPAMENTO";
  featured_image_url: string | null;
  seo_title: string | null;
  seo_description: string | null;
  published_at: string | null;
  author: { name: string; username: string };
};

export type AcademyPost = AcademyPostSummary & {
  content: string;
  video_url: string | null;
  equipment_specification: null | {
    rod_length_m: number | null;
    rod_construction: string | null;
    reel_size: number | null;
    main_line_material: string | null;
    main_line_diameter_mm: number | null;
    shock_leader_type: string | null;
    casting_weight_min_g: number | null;
    casting_weight_max_g: number | null;
    extra_specs: Record<string, unknown> | null;
  };
};

export type User = {
  id: number;
  name: string;
  username: string;
  email: string;
  role: "ADMIN" | "AUTHOR" | "USER";
  is_active: boolean;
};

export type CommunityComment = {
  id: number;
  content: string;
  author: { name: string; username: string; avatar_url: string | null };
  created_at: string;
};

export type CommunityThread = {
  id: number;
  title: string;
  content: string;
  category: "RELATO" | "DUVIDA" | "CAPTURA" | "EQUIPAMENTO";
  media_url: string | null;
  author: { name: string; username: string; avatar_url: string | null };
  beach: { name: string; slug: string } | null;
  comment_count: number;
  reaction_count: number;
  created_at: string;
  updated_at: string;
  comments?: CommunityComment[];
};

export type PublicAd = {
  id: number;
  placement: "HOME_TOPO" | "HOME_CONTEUDO" | "ACADEMIA" | "MAPA";
  title: string;
  image_url: string;
  target_url: string;
  alt_text: string;
};
