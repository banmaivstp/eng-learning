-- 1. Bảng Profiles (Nếu bạn chưa có, hãy chạy lệnh này)
CREATE TABLE IF NOT EXISTS public.profiles (
  id UUID REFERENCES auth.users ON DELETE CASCADE PRIMARY KEY,
  email TEXT,
  full_name TEXT,
  avatar_url TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Bảng Shows (Kênh Podcast)
CREATE TABLE public.shows (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  apple_show_url TEXT UNIQUE,
  title TEXT,
  cover_image TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Bảng Episodes (Tập Podcast)
CREATE TABLE public.episodes (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  show_id UUID REFERENCES public.shows(id) ON DELETE CASCADE,
  title TEXT,
  audio_url TEXT,
  transcript TEXT,
  quiz_json JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Bảng Learning History (Lịch sử làm bài)
CREATE TABLE public.learning_history (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
  episode_id UUID REFERENCES public.episodes(id) ON DELETE SET NULL,
  score INT,
  duration_seconds INT,
  completed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Bảng User Streaks (Chuỗi ngày học)
CREATE TABLE public.user_streaks (
  user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE PRIMARY KEY,
  current_streak INT DEFAULT 0,
  longest_streak INT DEFAULT 0,
  last_active_date DATE DEFAULT CURRENT_DATE
);

-- Cấp quyền cho bảng Profiles: User chỉ được xem và sửa thông tin của mình
CREATE POLICY "Users can view their own profile" ON public.profiles
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile" ON public.profiles
  FOR UPDATE USING (auth.uid() = id);

-- Cấp quyền cho bảng learning_history: Chỉ xem và thêm lịch sử của chính mình
CREATE POLICY "Users can view their own history" ON public.learning_history
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own history" ON public.learning_history
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Cấp quyền cho bảng user_streaks: Chỉ xem và sửa streak của mình
CREATE POLICY "Users can view their own streak" ON public.user_streaks
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update their own streak" ON public.user_streaks
  FOR ALL USING (auth.uid() = user_id);
  
-- Cấp quyền cho bảng episodes và shows: Mọi người đều có thể xem (để chọn bài học)
CREATE POLICY "Everyone can view shows" ON public.shows FOR SELECT USING (true);
CREATE POLICY "Everyone can view episodes" ON public.episodes FOR SELECT USING (true);



-- 1. Đảm bảo bảng profiles đã tồn tại
CREATE TABLE IF NOT EXISTS public.profiles (
  id UUID REFERENCES auth.users ON DELETE CASCADE PRIMARY KEY,
  email TEXT,
  full_name TEXT,
  avatar_url TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Tạo bảng Kênh Podcast (Bắt buộc chạy lệnh này)
CREATE TABLE IF NOT EXISTS public.shows (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  apple_show_url TEXT UNIQUE,
  title TEXT,
  cover_image TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Tạo bảng Tập Podcast (Bắt buộc chạy lệnh này)
CREATE TABLE IF NOT EXISTS public.episodes (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  show_id UUID REFERENCES public.shows(id) ON DELETE CASCADE,
  title TEXT,
  audio_url TEXT,
  transcript TEXT,
  quiz_json JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Tạo bảng Lịch sử làm bài
CREATE TABLE IF NOT EXISTS public.learning_history (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
  episode_id UUID REFERENCES public.episodes(id) ON DELETE SET NULL,
  score INT,
  duration_seconds INT,
  completed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Tạo bảng Chuỗi ngày học
CREATE TABLE IF NOT EXISTS public.user_streaks (
  user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE PRIMARY KEY,
  current_streak INT DEFAULT 0,
  longest_streak INT DEFAULT 0,
  last_active_date DATE DEFAULT CURRENT_DATE
);

-- ==========================================
-- 1. KÍCH HOẠT TÍNH NĂNG RLS CHO TẤT CẢ CÁC BẢNG
-- ==========================================
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.shows ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.episodes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.learning_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_streaks ENABLE ROW LEVEL SECURITY;

-- ==========================================
-- DỌN DẸP CÁC POLICY CŨ NẾU ĐÃ TỒN TẠI ĐỂ TRÁNH LỖI TRÙNG TÊN
-- ==========================================
DROP POLICY IF EXISTS "Allow anon/authenticated to insert/update profiles" ON public.profiles;
DROP POLICY IF EXISTS "Users can view their own profile" ON public.profiles;
DROP POLICY IF EXISTS "Everyone can view shows" ON public.shows;
DROP POLICY IF EXISTS "Everyone can view episodes" ON public.episodes;
DROP POLICY IF EXISTS "Allow application to insert/update shows" ON public.shows;
DROP POLICY IF EXISTS "Allow application to insert/update episodes" ON public.episodes;
DROP POLICY IF EXISTS "Users can view their own history" ON public.learning_history;
DROP POLICY IF EXISTS "Users can insert their own history" ON public.learning_history;
DROP POLICY IF EXISTS "Users can view their own streak" ON public.user_streaks;
DROP POLICY IF EXISTS "Users can update/insert their own streak" ON public.user_streaks;


-- ==========================================
-- 2. CẤP QUYỀN TRÊN BẢNG PROFILES (Thông tin học viên)
-- ==========================================
CREATE POLICY "Allow anon/authenticated to insert/update profiles" 
ON public.profiles FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Users can view their own profile" 
ON public.profiles FOR SELECT USING (auth.uid() = id);


-- ==========================================
-- 3. CẤP QUYỀN TRÊN BẢNG SHOWS & EPISODES (Dữ liệu bài học công khai)
-- ==========================================
CREATE POLICY "Everyone can view shows" 
ON public.shows FOR SELECT USING (true);

CREATE POLICY "Everyone can view episodes" 
ON public.episodes FOR SELECT USING (true);

CREATE POLICY "Allow application to insert/update shows" 
ON public.shows FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow application to insert/update episodes" 
ON public.episodes FOR ALL USING (true) WITH CHECK (true);


-- ==========================================
-- 4. CẤP QUYỀN TRÊN BẢNG LEARNING_HISTORY (Lịch sử làm bài)
-- ==========================================
CREATE POLICY "Users can view their own history" 
ON public.learning_history FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own history" 
ON public.learning_history FOR INSERT WITH CHECK (auth.uid() = user_id);


-- ==========================================
-- 5. CẤP QUYỀN TRÊN BẢNG USER_STREAKS (Chuỗi ngày học liên tục)
-- ==========================================
CREATE POLICY "Users can view their own streak" 
ON public.user_streaks FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update/insert their own streak" 
ON public.user_streaks FOR ALL USING (true) WITH CHECK (true);

ALTER TABLE episodes
ADD CONSTRAINT episodes_show_title_unique
UNIQUE(show_id, title);



-- Lệnh này không tạo file nhưng sẽ liệt kê cấu trúc các bảng
SELECT table_name, column_name, data_type 
FROM information_schema.columns 
WHERE table_schema = 'public';

-- =========================================================================
-- BƯỚC 1: XÓA SẠCH CÁC POLICY BẢO MẬT (RLS) ĐỂ TRÁNH XUNG ĐỘT ÉP KIỂU
-- =========================================================================

-- 1. Xóa các policy trên bảng profiles
DROP POLICY IF EXISTS "Users can update their own profile" ON public.profiles;
DROP POLICY IF EXISTS "Users can view their own profile" ON public.profiles;
DROP POLICY IF EXISTS "Enable insert for authenticated users only" ON public.profiles;
DROP POLICY IF EXISTS "Public profiles are viewable by everyone" ON public.profiles;

-- 2. Xóa các policy trên bảng learning_history
DROP POLICY IF EXISTS "Users can view their own history" ON public.learning_history;
DROP POLICY IF EXISTS "Users can insert their own history" ON public.learning_history;

-- 3. Xóa các policy trên bảng user_streaks
DROP POLICY IF EXISTS "Users can view their own streak" ON public.user_streaks;
DROP POLICY IF EXISTS "Users can update their own streak" ON public.user_streaks;


-- =========================================================================
-- BƯỚC 2: XÓA CÁC RÀNG BUỘC KHÓA NGOẠI (FOREIGN KEYS) HIỆN TẠI
-- =========================================================================

-- Xóa liên kết mặc định giữa profiles và bảng auth hệ thống (nếu có)
ALTER TABLE IF EXISTS public.profiles DROP CONSTRAINT IF EXISTS profiles_id_fkey;

-- Xóa liên kết khóa ngoại giữa các bảng nghiệp vụ
ALTER TABLE IF EXISTS public.learning_history DROP CONSTRAINT IF EXISTS learning_history_user_id_fkey;
ALTER TABLE IF EXISTS public.user_streaks DROP CONSTRAINT IF EXISTS user_streaks_user_id_fkey;


-- =========================================================================
-- BƯỚC 3: CHUYỂN ĐỔI ĐỒNG LOẠT KIỂU DỮ LIỆU TỪ UUID SANG TEXT
-- =========================================================================

ALTER TABLE public.profiles ALTER COLUMN id TYPE text USING id::text;
ALTER TABLE public.learning_history ALTER COLUMN user_id TYPE text USING user_id::text;
ALTER TABLE public.user_streaks ALTER COLUMN user_id TYPE text USING user_id::text;


-- =========================================================================
-- BƯỚC 4: TẠO LẠI CÁC KHÓA NGOẠI KẾT NỐI MỚI (DÙNG KIỂU TEXT)
-- =========================================================================

ALTER TABLE public.learning_history
ADD CONSTRAINT learning_history_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES public.profiles(id) ON DELETE CASCADE;

ALTER TABLE public.user_streaks
ADD CONSTRAINT user_streaks_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES public.profiles(id) ON DELETE CASCADE;


-- =========================================================================
-- BƯỚC 5: THÊM CỘT total_score CHO BẢNG profiles (Sửa lỗi thiếu cột tính điểm)
-- =========================================================================

ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS total_score integer NOT NULL DEFAULT 0;


-- =========================================================================
-- BƯỚC 6: TẠO LẠI CÁC POLICY RLS ĐỒNG BỘ KIỂU TEXT (SỬ DỤNG auth.uid()::text)
-- =========================================================================

-- --- Cấu hình bảo mật bảng profiles ---
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public profiles are viewable by everyone" ON public.profiles FOR SELECT USING (true);
CREATE POLICY "Users can update their own profile" ON public.profiles FOR UPDATE USING (auth.uid()::text = id);
CREATE POLICY "Enable insert for authenticated users only" ON public.profiles FOR INSERT WITH CHECK (auth.uid()::text = id);

-- --- Cấu hình bảo mật bảng learning_history ---
ALTER TABLE public.learning_history ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view their own history" ON public.learning_history FOR SELECT USING (auth.uid()::text = user_id);
CREATE POLICY "Users can insert their own history" ON public.learning_history FOR INSERT WITH CHECK (auth.uid()::text = user_id);

-- --- Cấu hình bảo mật bảng user_streaks ---
ALTER TABLE public.user_streaks ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view their own streak" ON public.user_streaks FOR SELECT USING (auth.uid()::text = user_id);
CREATE POLICY "Users can update their own streak" ON public.user_streaks FOR UPDATE USING (auth.uid()::text = user_id);

-- Đảm bảo trường completed_at tự động sinh mốc thời gian UTC chính xác
ALTER TABLE public.learning_history 
  ALTER COLUMN completed_at SET DEFAULT timezone('utc'::text, now());
  
-- Thêm cột created_at với kiểu dữ liệu thời gian và tự động điền thời gian hiện tại khi thêm bản ghi mới
ALTER TABLE public.learning_history 
ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();