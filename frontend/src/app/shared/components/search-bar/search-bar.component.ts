import { Component, OnInit, OnDestroy, Output, EventEmitter, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { Subject, Subscription } from 'rxjs';
import { debounceTime, distinctUntilChanged, switchMap } from 'rxjs/operators';
import { ProductService } from '../../../core/services/product.service';
import { Product } from '../../../core/models/product.model';
import { SearchOverlayComponent } from '../search-overlay/search-overlay.component';
import { ClickOutsideDirective } from '../../directives/click-outside.directive';

@Component({
  selector: 'app-search-bar',
  standalone: true,
  imports: [CommonModule, SearchOverlayComponent, ClickOutsideDirective],
  templateUrl: './search-bar.component.html',
  styleUrl: './search-bar.component.scss'
})
export class SearchBarComponent implements OnInit, OnDestroy {
  @Output() searchSubmitted = new EventEmitter<string>();

  query = '';
  results: Product[] = [];
  isLoading = false;
  isOverlayOpen = false;

  private searchSubject = new Subject<string>();
  private searchSubscription!: Subscription;

  @ViewChild(SearchOverlayComponent) overlay!: SearchOverlayComponent;

  constructor(
    private productService: ProductService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.searchSubscription = this.searchSubject.pipe(
      debounceTime(350),
      distinctUntilChanged(),
      switchMap(term => {
        if (term.length >= 2) {
          this.isLoading = true;
          return this.productService.getProducts({ search: term, page_size: 5 });
        } else {
          this.results = [];
          this.isLoading = false;
          return [];
        }
      })
    ).subscribe({
      next: (res: any) => {
        const products = Array.isArray(res) ? res : (res.results || []);
        this.results = products;
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
        this.results = [];
      }
    });
  }

  ngOnDestroy(): void {
    if (this.searchSubscription) {
      this.searchSubscription.unsubscribe();
    }
  }

  onInput(event: Event): void {
    const input = event.target as HTMLInputElement;
    this.query = input.value;
    this.isOverlayOpen = this.query.length >= 2;
    this.searchSubject.next(this.query);
  }

  onFocus(): void {
    if (this.query.length >= 2) {
      this.isOverlayOpen = true;
    }
  }

  onKeyDown(event: KeyboardEvent): void {
    if (event.key === 'Enter') {
      this.submitSearch();
    } else if (event.key === 'Escape') {
      this.closeOverlay();
    } else if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
      if (this.isOverlayOpen && this.overlay) {
        this.overlay.handleKeyDown(event);
      }
    }
  }

  submitSearch(): void {
    if (this.query.trim()) {
      this.searchSubmitted.emit(this.query);
      this.router.navigate(['/catalog'], { queryParams: { search: this.query } });
      this.closeOverlay();
    }
  }

  onResultSelected(product: Product): void {
    this.router.navigate(['/products', product.slug]);
    this.closeOverlay();
    this.query = '';
  }

  closeOverlay(): void {
    this.isOverlayOpen = false;
  }
}
