import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, User, Eye, EyeOff, CheckCircle } from 'lucide-react';
import { useAuthStore } from '../services/authService';

const SignupPage: React.FC = () => {
  const navigate = useNavigate();
  const { register, isLoading } = useAuthStore();
  
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [localLoading, setLocalLoading] = useState(false);

  const passwordChecks = [
    { label: 'At least 8 characters', met: formData.password.length >= 8 },
    { label: 'One uppercase letter', met: /[A-Z]/.test(formData.password) },
    { label: 'One lowercase letter', met: /[a-z]/.test(formData.password) },
    { label: 'One number', met: /[0-9]/.test(formData.password) },
  ];

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validate passwords match
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    // Validate password strength
    if (!passwordChecks.every(c => c.met)) {
      setError('Password does not meet requirements');
      return;
    }

    setLocalLoading(true);

    try {
      await register(formData.email, formData.name, formData.password, formData.confirmPassword);
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Registration failed. Please try again.');
    } finally {
      setLocalLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 py-12 px-4">
      <div className="max-w-md w-full">
        {/* Logo/Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 bg-clip-text text-transparent mb-2">
            🧵 Dress AI
          </h1>
          <p className="text-gray-600 font-medium">Your Personal Fashion Assistant</p>
        </div>

        {/* Signup Card */}
        <div className="bg-white/80 backdrop-blur-lg rounded-3xl shadow-2xl p-8 border border-white/50">
          <h2 className="text-2xl font-bold text-gray-800 text-center mb-2">Create Account</h2>
          <p className="text-gray-500 text-center mb-6">Start your fashion journey today</p>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-600 rounded-xl text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Name */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Full Name
              </label>
              <div className="relative group">
                <User className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 group-focus-within:text-purple-500 transition-colors h-5 w-5" />
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  className="w-full pl-12 pr-4 py-3.5 bg-gray-50 border-2 border-gray-100 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all outline-none"
                  placeholder="John Doe"
                  required
                />
              </div>
            </div>

            {/* Email */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Email Address
              </label>
              <div className="relative group">
                <Mail className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 group-focus-within:text-purple-500 transition-colors h-5 w-5" />
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="w-full pl-12 pr-4 py-3.5 bg-gray-50 border-2 border-gray-100 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all outline-none"
                  placeholder="you@example.com"
                  required
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Password
              </label>
              <div className="relative group">
                <Lock className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 group-focus-within:text-purple-500 transition-colors h-5 w-5" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  className="w-full pl-12 pr-14 py-3.5 bg-gray-50 border-2 border-gray-100 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all outline-none"
                  placeholder="Create a password"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-purple-500 transition-colors"
                >
                  {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                </button>
              </div>
              
              {/* Password Strength */}
              <div className="mt-3 space-y-1">
                {passwordChecks.map((check, idx) => (
                  <div key={idx} className="flex items-center text-xs">
                    <CheckCircle 
                      className={`h-3.5 w-3.5 mr-2 ${
                        check.met ? 'text-green-500' : 'text-gray-300'
                      }`} 
                    />
                    <span className={check.met ? 'text-green-600 font-medium' : 'text-gray-500'}>
                      {check.label}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Confirm Password */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Confirm Password
              </label>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  className={`w-full pl-12 pr-4 py-3.5 bg-gray-50 border-2 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all outline-none ${
                    formData.confirmPassword && formData.password !== formData.confirmPassword
                      ? 'border-red-300' : 'border-gray-100'
                  }`}
                  placeholder="Confirm your password"
                  required
                />
              </div>
              {formData.confirmPassword && formData.password !== formData.confirmPassword && (
                <p className="mt-1.5 text-xs text-red-500">Passwords do not match</p>
              )}
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={isLoading || localLoading}
              className="w-full py-3.5 px-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold rounded-xl hover:from-purple-700 hover:to-pink-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-purple-500/25 mt-2"
            >
              {isLoading || localLoading ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-2 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Creating account...
                </span>
              ) : (
                'Create Account'
              )}
            </button>
          </form>

          {/* Sign In Link */}
          <p className="mt-6 text-center text-gray-600">
            Already have an account?{' '}
            <Link to="/login" className="text-purple-600 hover:text-purple-700 font-semibold transition-colors">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default SignupPage;
