# Milestone 6: Mobile Client Integration (Android)

**Goal**: Seamlessly transition from a web UI to a native Android Kotlin application to strictly comply with the Hackathon Mobile Mandate. The app directly communicates with the Python Orchestrator backend via `http://10.0.2.2:8000`.

## Phase 1: Native Scaffolding & Layouts
- [x] T001 Scaffold directory structure for `mobile/android_client/`
- [x] T002 Implement `activity_main.xml` with Material Design input components, ScrollView, and modular TextViews for pipeline results.
- [x] T003 Ensure `AndroidManifest.xml` possesses `android.permission.INTERNET` and `android:usesCleartextTraffic="true"` to hit localhost during emulator testing.

## Phase 2: Kotlin Network Integration
- [x] T004 Build `MainActivity.kt` orchestrator network controller.
- [x] T005 Implement asynchronous `HttpURLConnection` coroutines hitting POST `/api/orchestrate/run-all`.
- [x] T006 Safely parse nested `JSONObjects` (parsed_intent, assigned_provider, price_breakdown, booking_summary) on the Main Thread.
- [x] T007 Handle rollback HTTP 400 structures and network failure exceptions elegantly inside an error `TextView`.

## Phase 3: Build & Execution Checklist (Developer Handoff)
- [ ] T008 **Create Android Studio Project**: Open Android Studio -> New Project -> Empty Activity.
- [ ] T009 **Copy Assets**: Copy the generated `MainActivity.kt`, `activity_main.xml`, and `AndroidManifest.xml` directly into the initialized workspace.
- [ ] T010 **Add Coroutines Dependency**: Ensure `implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")` is inside `build.gradle.kts`.
- [ ] T011 **Run Local Uvicorn Backend**: Ensure `uvicorn main:app --host 0.0.0.0 --port 8000` is running on the host machine.
- [ ] T012 **Boot Emulator**: Launch Pixel emulator and test end-to-end Roman Urdu query generation.
