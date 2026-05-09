import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { UiService } from '../../../core/services/ui.service';
import { ConfigService } from '../../../core/services/config';

@Component({
  selector: 'app-footer',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './footer.component.html',
  styleUrl: './footer.component.scss',
})
export class FooterComponent {
  private uiService = inject(UiService);
  private configService = inject(ConfigService);
  
  currentYear = new Date().getFullYear();

  readonly shopLinks = this.configService.footerLinks.shop;
  readonly helpLinks = this.configService.footerLinks.help;
  readonly contactInfo = this.configService.footerLinks.contact;

  showComingSoon(feature: string): void {
    this.uiService.showComingSoon(feature);
  }
}
