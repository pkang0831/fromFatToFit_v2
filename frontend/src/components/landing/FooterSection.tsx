'use client';

import Link from 'next/link';

export function FooterSection() {
  return (
    <footer className="bg-text py-16 px-6">
      <div className="max-w-6xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-10 mb-12">
          <div className="md:col-span-1">
            <h3 className="text-xl font-bold text-white mb-3">FromFatToFit</h3>
            <p className="text-white/50 text-sm leading-relaxed">
              AI-powered fitness tracking to help you achieve your body transformation goals.
            </p>
          </div>

          <div>
            <h4 className="text-white font-semibold mb-4 text-sm uppercase tracking-wider">Product</h4>
            <ul className="space-y-2">
              {['Features', 'Pricing', 'FAQ'].map((item) => (
                <li key={item}>
                  <a href={`#${item.toLowerCase()}`} className="text-white/50 hover:text-white text-sm transition-colors">
                    {item}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h4 className="text-white font-semibold mb-4 text-sm uppercase tracking-wider">Account</h4>
            <ul className="space-y-2">
              {[
                { label: 'Sign In', href: '/login' },
                { label: 'Register', href: '/register' },
              ].map((item) => (
                <li key={item.label}>
                  <Link href={item.href} className="text-white/50 hover:text-white text-sm transition-colors">
                    {item.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h4 className="text-white font-semibold mb-4 text-sm uppercase tracking-wider">Legal</h4>
            <ul className="space-y-2">
              {['Privacy Policy', 'Terms of Service'].map((item) => (
                <li key={item}>
                  <span className="text-white/50 text-sm cursor-default">{item}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="border-t border-white/10 pt-8 text-center">
          <p className="text-white/40 text-sm">
            &copy; {new Date().getFullYear()} FromFatToFit. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}
