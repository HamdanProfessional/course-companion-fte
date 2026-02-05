'use client';

import { useState, useEffect } from 'react';

/**
 * Custom hook to safely use localStorage without hydration errors.
 *
 * Solves the "Text content did not match" error by ensuring
 * localStorage is only accessed after component mount on the client.
 *
 * @param key - The localStorage key to read/write
 * @param initialValue - Default value if key doesn't exist
 * @returns [storedValue, setValue] tuple like useState
 */
export function useLocalStorage<T>(key: string, initialValue: T) {
  // Initialize state with initialValue (prevents SSR mismatch)
  const [storedValue, setStoredValue] = useState<T>(initialValue);
  const [isInitialized, setIsInitialized] = useState(false);

  // After component mounts, read from localStorage
  useEffect(() => {
    try {
      const item = window.localStorage.getItem(key);
      if (item) {
        // Parse JSON for objects/arrays, otherwise use as-is
        try {
          setStoredValue(JSON.parse(item));
        } catch {
          // Not JSON, use raw value
          setStoredValue(item as unknown as T);
        }
      }
    } catch (error) {
      console.error(`Error reading localStorage key "${key}":`, error);
    } finally {
      setIsInitialized(true);
    }
  }, [key]);

  // Return a wrapped version of useState's setter function
  const setValue = (value: T | ((val: T) => T)) => {
    try {
      // Allow value to be a function so we have same API as useState
      const valueToStore = value instanceof Function ? value(storedValue) : value;

      // Save state
      setStoredValue(valueToStore);

      // Save to localStorage
      if (typeof window !== 'undefined') {
        window.localStorage.setItem(key, JSON.stringify(valueToStore));
      }
    } catch (error) {
      console.error(`Error setting localStorage key "${key}":`, error);
    }
  };

  return [storedValue, setValue] as const;
}

/**
 * Simplified version for string values (no JSON parsing)
 */
export function useLocalStorageString(key: string, initialValue: string) {
  const [storedValue, setStoredValue] = useState<string>(initialValue);
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    try {
      const item = window.localStorage.getItem(key);
      if (item) {
        setStoredValue(item);
      }
    } catch (error) {
      console.error(`Error reading localStorage key "${key}":`, error);
    } finally {
      setIsInitialized(true);
    }
  }, [key]);

  const setValue = (value: string | ((val: string) => string)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);

      if (typeof window !== 'undefined') {
        window.localStorage.setItem(key, valueToStore);
      }
    } catch (error) {
      console.error(`Error setting localStorage key "${key}":`, error);
    }
  };

  return [storedValue, setValue] as const;
}
