import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Product } from '../models/product.model';

@Injectable({
  providedIn: 'root',
})
export class ProductService {
  private apiUrl = `${environment.apiUrl}/products/products/`;

  constructor(private http: HttpClient) {}

  getProducts(params?: {
    ordering?: string;
    category?: string;
    min_price?: number;
    max_price?: number;
    availability?: boolean;
    search?: string;
    page?: number;
    page_size?: number;
  }): Observable<Product[]> {
    let httpParams = new HttpParams();

    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          httpParams = httpParams.append(key, value.toString());
        }
      });
    }

    return this.http.get<Product[]>(this.apiUrl, { params: httpParams });
  }

  getProductBySlug(slug: string): Observable<Product> {
    return this.http.get<Product>(`${this.apiUrl}${slug}/`);
  }
}
