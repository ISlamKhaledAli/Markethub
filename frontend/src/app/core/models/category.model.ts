export interface Category {
  id: number;
  name: string;
  slug: string;
  parent?: number | null;
  image?: string;
  subcategories: Category[];
  created_at: string;
}
