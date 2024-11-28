"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import LoginForm from "@/app/ui/login-form";

export default function LoginPage() {
  /*const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const router = useRouter();

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    try {
      // TODO: Implement actual login logic here
      console.log("Login attempt with:", email, password);
    } catch (err) {
      console.log(err);
      setError("Login failed. Please check your credentials.");
    }
  };*/

  return <LoginForm />;
}
