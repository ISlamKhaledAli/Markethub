import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-newsletter',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './newsletter.component.html',
  styleUrl: './newsletter.component.scss',
})
export class NewsletterComponent {
  email = '';
  isSubmitting = false;
  successMessage = '';
  errorMessage = '';

  onSubscribe(): void {
    if (!this.email || !this.email.includes('@')) {
      this.errorMessage = 'Please enter a valid email address.';
      return;
    }
    
    this.isSubmitting = true;
    this.errorMessage = '';
    this.successMessage = '';
    
    // TODO: Connect to newsletter API endpoint when available
    // For now, process immediately to avoid simulated delays
    this.isSubmitting = false;
    this.successMessage = "You're on the list! Welcome to the Nexus Circle.";
    this.email = '';
  }
}
