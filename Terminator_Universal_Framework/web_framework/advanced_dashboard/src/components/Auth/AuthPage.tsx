import { useState } from 'react';
import { LoginForm } from './LoginForm';
import { SignupForm } from './SignupForm';

export function AuthPage() {
  const [mode, setMode] = useState<'login' | 'signup'>('login');

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-gray-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {mode === 'login' ? <LoginForm /> : <SignupForm />}

        <div className="text-center mt-4">
          <button
            onClick={() => setMode(mode === 'login' ? 'signup' : 'login')}
            className="text-sm text-blue-600 hover:text-blue-700 hover:underline"
          >
            {mode === 'login'
              ? "Don't have an account? Sign up"
              : 'Already have an account? Sign in'}
          </button>
        </div>
      </div>
    </div>
  );
}
