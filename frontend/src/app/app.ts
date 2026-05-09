import { Component, OnInit, inject } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { NavbarComponent } from './shared/components/navbar/navbar';

import { FooterComponent } from './shared/components/footer/footer.component';
import { environment } from '../environments/environment';
import { UiService } from './core/services/ui.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    RouterOutlet, 
    NavbarComponent, 
    FooterComponent,
    MatSnackBarModule
  ],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App implements OnInit {
  private http = inject(HttpClient);
  private uiService = inject(UiService);

  ngOnInit(): void {
    this.checkApiHealth();
  }

  private checkApiHealth(): void {
    this.http.get(`${environment.apiUrl}/products/products/?page_size=1`).subscribe({
      next: () => console.log('✅ API connection healthy'),
      error: (err) => {
        console.warn('⚠️ API unreachable:', err.message);
        this.uiService.showInfo('API connection issue. Some features may not work.');
      }
    });
  }

  showComingSoon(feature: string): void {
    this.uiService.showComingSoon(feature);
  }
}
