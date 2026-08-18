import js from "@eslint/js";
import tsParser from "@typescript-eslint/parser";
import tsLint from "@typescript-eslint/eslint-plugin";
import globals from "globals";
import reactHooks from "eslint-plugin-react-hooks";

/** @type {import("eslint").Linter.FlatConfig[]} */
export default [
  {
    ignores: ["dist"],
  },
  {
    files: ["**/*.{ts,tsx}"],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: "module",
      parser: tsParser,
      globals: { ...globals.browser, ...globals.node },
    },
    plugins: {
      "@typescript-eslint": tsLint,
      "react-hooks": reactHooks,
    },
    rules: {
      ...js.configs.recommended.rules,
      ...tsLint.configs.recommended.rules,
      ...reactHooks.configs.recommended.rules,
      // TypeScript já cobre identificadores não definidos (incluindo tipos
      // ambientes do DOM como RequestInit) com mais precisão que o ESLint
      // base, que não enxerga esses globais e gera falso positivo.
      "no-undef": "off",
    },
  },
];
