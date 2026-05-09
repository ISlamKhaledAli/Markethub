import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class ConfigService {

  // Navbar Configuration
  readonly navLinks = [
    { label: 'Shop', route: '/catalog', queryParams: { view: 'all' } },
    { label: 'Categories', route: '/catalog', queryParams: { view: 'categories' } },
    { label: 'Lookbook', feature: 'Lookbook' },
    { label: 'About', feature: 'About' }
  ];

  // Footer Configuration
  readonly footerLinks = {
    shop: [
      { label: 'New Arrivals', route: '/catalog', queryParams: { ordering: '-created_at' } },
      { label: 'Best Sellers', route: '/catalog', queryParams: { ordering: '-created_at' } },
      { label: 'Collections', route: '/catalog', queryParams: {} },
      { label: 'Sale', route: '/catalog', queryParams: { min_price: 0, max_price: 100 } }
    ],
    help: [
      { label: 'Privacy Policy', feature: 'Privacy Policy' },
      { label: 'Terms of Service', feature: 'Terms of Service' },
      { label: 'Shipping Info', feature: 'Shipping Info' },
      { label: 'Returns', feature: 'Returns' }
    ],
    contact: {
      address: '123 Commerce Way, Nexus Park, CA 90210',
      email: 'support@nexuscommerce.com',
      phone: '+1 (800) NEXUS-HQ',
      socials: [
        { name: 'Public', icon: 'public', feature: 'Social' },
        { name: 'Share', icon: 'share', feature: 'Social' },
        { name: 'Mail', icon: 'mail', feature: 'Contact' }
      ]
    }
  };

  // Home Page Configuration
  readonly homeConfig = {
    hero: {
      badge: 'New Arrivals',
      title: 'Defining the New Standard.',
      subtitle: 'Summer Collection 2026',
      description: 'Discover our curated arrivals designed for modern living. Precision-crafted essentials that bridge the gap between utility and luxury.',
      image: 'https://lh3.googleusercontent.com/aida-public/AB6AXuDziO1l-bCgTE_FnyHagml6xf9Nj1xt_KP2AL33Rs57k_FgHm05gyUIdk6Vck6IdDOAEuS0qvMzRF_FQBWbvqFFiPvJn0ln74bvAcXaoeKZnJxKh6v5PZtedJ6TK8Lho462creZUryz1VqCI4NT2s2OQG4BTmlVsKEzybivG2hWNh9xk-TvxhBiByFY_ictSJ9NGipNlTwm5UhgN6TrMg6LpaiR_WtS1E20fxN_6RWp3hFmKYEtnMJcigfdH0fQ7__XrX5ONdgasQ4',
      ctaText: 'Shop New Arrivals',
      link: '/catalog'
    }
  };

  // Catalog Configuration
  readonly catalogConfig = {
    defaultPageSize: 12,
    defaultOrdering: '-created_at',
    placeholders: {
      productImage: 'https://placehold.co/600x800/e2e8f0/475569?text=Product+Image'
    }
  };
}
