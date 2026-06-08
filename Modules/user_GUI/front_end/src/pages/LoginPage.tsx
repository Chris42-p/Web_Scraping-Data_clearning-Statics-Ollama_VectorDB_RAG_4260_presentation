import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
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
        <div>
            <h1>Login Page</h1>

            <form onSubmit={handleSubmit}>
                <div>
                    <label>Username: </label>
                    <input
                        type="text"
                        value={username}
                        onChange={(event) => setUsername(event.target.value)}
                    />
                </div>

                <div>
                    <label>Password: </label>
                    <input
                        type="password"
                        value={password}
                        onChange={(event) => setPassword(event.target.value)}
                    />
                </div>

                {errorMessage && <p style={{ color: "red" }}>{errorMessage}</p>}
                {successMessage && <p style={{ color: "green" }}>{successMessage}</p>}

                <button type="submit" disabled={loading}>
                    {loading ? "Logging in..." : "Login"}
                </button>
            </form>
        </div>
    );
}