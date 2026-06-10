import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { loginUser } from "../services";

export function LoginPage() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [loading, setLoading] = useState(false);
    const [errorMessage, setErrorMessage] = useState("");
    const [successMessage, setSuccessMessage] = useState("");
    const navigate = useNavigate();

    async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
        event.preventDefault();

        setLoading(true);
        setErrorMessage("");
        setSuccessMessage("");

        try {
            await loginUser({
                username: username.trim(),
                password: password.trim(),
            });

            setSuccessMessage("Login successful.");
            navigate("/app/dashboard", { replace: true });
        } catch (error) {
            console.error("Login failed:", error);
            setErrorMessage(
                error instanceof Error
                    ? error.message
                    : "Login failed. Please check your username and password."
            );
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="auth-page">
            <div className="auth-card">
                <h1>Login</h1>
                <p>Access the Vancouver rental market workspace.</p>

                <form onSubmit={handleSubmit} className="auth-form">
                    <div>
                        <label>Username</label>
                        <input
                            type="text"
                            value={username}
                            onChange={(event) => setUsername(event.target.value)}
                        />
                    </div>

                    <div>
                        <label>Password</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(event) => setPassword(event.target.value)}
                        />
                    </div>

                    {errorMessage && <p className="auth-error">{errorMessage}</p>}
                    {successMessage && <p className="auth-success">{successMessage}</p>}

                    <button type="submit" disabled={loading}>
                        {loading ? "Logging in..." : "Login"}
                    </button>
                </form>

                <p className="auth-switch-text">
                    Don’t have an account? <Link to="/register">Create one</Link>
                </p>
            </div>
        </div>
    );
}