Created At: 2026-06-23T09:06:23Z
Completed At: 2026-06-23T09:06:23Z
File Path: `file:///Users/piyush/Downloads/Piyush%20SUraag%202/app.py`
Total Lines: 2491
Total Bytes: 125218
Showing lines 216 to 1015
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
216:     background: linear-gradient(90deg, var(--accent-neon), var(--accent-cyan));
217:     transform: scaleX(0);
218:     transition: transform 0.3s;
219: }}
220: [data-testid="stMetric"]:hover::before {{
221:     transform: scaleX(1);
222: }}
223: [data-testid="stMetricLabel"] {{
224:     color: var(--text-muted) !important;
225:     font-size: 11px !important;
226:     font-weight: 700 !important;
227:     text-transform: uppercase;
228:     letter-spacing: 1px;
229:     font-family: 'monospace', monospace;
230: }}
231: [data-testid="stMetricValue"] {{
232:     color: var(--text-primary) !important;
233:     font-size: 32px !important;
234:     font-weight: 800 !important;
235:     font-family: 'Inter', sans-serif;
236:     text-shadow: 0 0 20px rgba(255, 255, 255, 0.1);
237: }}
238: 
239: /* ── Modern Alert Styling ──────────────────────────────────── */
240: .stAlert {{
241:     border-radius: 16px;
242:     border: none;
243:     animation: fadeInUp 0.5s ease-out both;
244:     backdrop-filter: blur(10px);
245:     box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
246: }}
247: 
248: /* ── Enhanced Input Fields ─────────────────────────────────── */
249: .stTextInput > div > div > input {{
250:     background: linear-gradient(135deg, var(--surface-800), var(--muted-700));
251:     color: var(--text-primary);
252:     border: 1px solid var(--border-subtle);
253:     border-radius: 12px;
254:     font-family: 'Inter', sans-serif;
2
<truncated 36662 bytes>
  df, error = load_and_validate(uploaded_file.getvalue(), uploaded_file.name)
975: 
976:         if error:
977:             st.error(f"❌ **File Error:** {error}")
978:             st.stop()
979: 
980:         # Extract phone numbers from Subscriber_ID
981:         df['Phone_Number'] = df['Subscriber_ID'].str.extract(r'(\d{10})$')[0]
982:         
983:         # Convert Timestamp to datetime
984:         df['Timestamp'] = pd.to_datetime(df['Timestamp'])
985:         
986:         # Store original dataframe
987:         df_original = df.copy()
988: 
989:         # ── ADVANCED SEARCH/FILTER SECTION ────────────────────
990:         section_header(
991:             "🔍 Advanced Search & Filters",
992:             "Filter IPDR data by IP address, protocol, service type, destination port, bytes transferred, and date range",
993:             "🔎"
994:         )
995:         
996:         with st.expander("🔎 Search & Filter Options", expanded=True):
997:             col1, col2, col3, col4 = st.columns(4)
998:             
999:             with col1:
1000:                 st.markdown("**🌐 Source IP Address**")
1001:                 source_ip_search = st.text_input(
1002:                     "Enter Source IP",
1003:                     placeholder="e.g., 192.168.1.10",
1004:                     key="source_ip_search",
1005:                     label_visibility="collapsed"
1006:                 )
1007:                 
1008:                 st.markdown("**🌐 Destination IP Address**")
1009:                 dest_ip_search = st.text_input(
1010:                     "Enter Destination IP",
1011:                     placeholder="e.g., 8.8.8.8",
1012:                     key="dest_ip_search",
1013:                     label_visibility="collapsed"
1014:                 )
1015:             
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.
