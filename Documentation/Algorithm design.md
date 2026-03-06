# Design Document: Sentinel-JP (Privacy Gateway)
- ## 1. Executive Summary
  
  **Sentinel-JP** is a local-first application designed to enable secure use of cloud-based LLMs (e.g., Claude, GPT-4) within regulated industries. It uses a **Zero-Knowledge** architecture where PII/PCI/PHI is redacted on the user's device and replaced with high-entropy, dynamic pseudonyms. The re-identification key never leaves the client’s volatile memory.
- ## 2. System Architecture
  
  The system follows a **"Man-in-the-Browser/App"** pattern.
- ### 2.1 Component Overview
- **Inference Engine (Local):** A WASM-compiled **Sudachi.rs + GiNZA** pipeline for Japanese morphological analysis and NER.
- **Vault (Local):** An in-memory Key-Value store (RAM-only) mapping UIDs to original PII.
- **Rule Engine:** Generates a unique "Secret Pattern" (e.g., `&%[...]%&`) for each thread.
- **Streaming Interceptor:** A state-machine buffer that swaps UIDs in the incoming LLM response stream.
  
  ---
- ## 3. The Anonymization Algorithm (Outbound)
- ### Step 1: Thread Initialization
  
  A **Session Secret** is generated.
- **Pattern:** `&%[` + `TYPE_CHAR` + `-` + `HEX_ID` + `]%&`
- **Example Rule:** `Person = P`, `Location = L`.
- ### Step 2: Local Scan (The "Scrubber")
  
  The prompt is processed locally:
- **Tokenization:** Text is split using Sudachi (A-mode) for speed.
- **Entity Recognition:** GiNZA identifies entities (Person, Org, Place, etc.).
- **UID Assignment:** Every unique entity is assigned a random 4-character HEX.
- **Mapping:** The Vault stores: `{"&%[P-u7d2]%&": "田中太郎"}`.
- ### Step 3: Prompt Construction
  
  A **System Instruction** is prepended to the user's prompt:
  
  > "System: User input is pseudonymized. Patterns `&%[P-...]%&` are PEOPLE; `&%[L-...]%&` are PLACES. Maintain these markers exactly in your response."
  
  ---
- ## 4. The Streaming Re-identification Algorithm (Inbound)
  
  To ensure zero-latency "feel," the app uses a **Structural State-Machine Buffer** instead of a time-based one.
- ### 4.1 State Machine Logic
- **State: PASS_THROUGH (Default)**
	- Tokens from the LLM are rendered immediately to the UI.
	- *Trigger:* If token contains `&`, move to **BUFFERING**.
- **State: BUFFERING**
	- Incoming tokens are diverted to a local `temp_buffer`.
	- *Check:* If `temp_buffer` matches `&%[...-...]%&`:
		- **Action:** Lookup the string in the **Local Vault**.
		- **Action:** Push the *original* PII to the UI.
		- **Action:** Reset to **PASS_THROUGH**.
	- *Safety:* If `temp_buffer` length > 25 chars without a closing `%&`:
		- **Action:** Push raw `temp_buffer` to UI (False Positive).
		- **Action:** Reset to **PASS_THROUGH**.
		  
		  ---
- ## 5. Security & Performance Specifications
- ### 5.1 Latency Targets (2026 Baseline)
  
  | Operation | Target Latency | Notes |
  | ---- | ---- | ---- |
  | **Local NER Scan** | < 120ms | Optimized via Rust-WASM. |
  | **UID Generation** | < 1ms | Cryptographically secure pseudo-random. |
  | **UI Re-ID Lag** | < 5ms | Instantaneous Find-and-Replace. |
  | **Total Overhead** | **~125ms** | Well below the human "real-time" threshold. |
- ### 5.2 Privacy Guarantees
- **Data Residency:** 100% of PII stays on the local CPU/RAM.
- **Zero Persistence:** The **Vault** is cleared when the tab/app is closed.
- **Entropy:** Dynamic markers (`&%[`, `]%&`) prevent collision with Markdown or Code blocks.
  
  ---
- ## 6. Attachment Processing
  
  Attachments follow the same logic but include an **OCR/Extraction** pre-step:
- **Extract:** PDF/Excel/Img text is extracted locally.
- **Scrub:** Text is pseudonymized.
- **Re-build:** A "Clean" `.txt` or `.md` version is sent to the LLM.
- **Reference:** The App maintains the link between the "Clean" file and the "Local" original.