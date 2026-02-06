'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, XCircle, AlertCircle, X } from 'lucide-react';
import { useEffect, useState } from 'react';

interface ToastProps {
  message: string;
  type: 'success' | 'error' | 'warning';
  duration?: number;
  onClose: () => void;
}

export function Toast({ message, type, duration = 3000, onClose }: ToastProps) {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(false);
      setTimeout(onClose, 300);
    }, duration);
    return () => clearTimeout(timer);
  }, [duration, onClose]);

  const icons = {
    success: <CheckCircle className="text-green-400" />,
    error: <XCircle className="text-red-400" />,
    warning: <AlertCircle className="text-amber-400" />,
  };

  const gradients = {
    success: 'from-green-500/20 to-emerald-500/20 border-green-500/30',
    error: 'from-red-500/20 to-rose-500/20 border-red-500/30',
    warning: 'from-amber-500/20 to-orange-500/20 border-amber-500/30',
  };

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, x: 100, scale: 0.8 }}
          animate={{ opacity: 1, x: 0, scale: 1 }}
          exit={{ opacity: 0, x: 100, scale: 0.8 }}
          transition={{ type: 'spring', stiffness: 200, damping: 20 }}
          className={`fixed top-4 right-4 z-50 p-4 rounded-xl border backdrop-blur-xl
                      bg-gradient-to-br ${gradients[type]} shadow-2xl`}
        >
          <div className="flex items-center gap-3">
            {icons[type]}
            <p className="text-white font-medium">{message}</p>
            <button onClick={onClose} className="ml-2 hover:scale-110 transition-transform">
              <X className="text-gray-400" />
            </button>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
